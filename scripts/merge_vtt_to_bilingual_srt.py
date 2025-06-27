# merge_vtt_to_bilingual_srt.py
# 新策略：按句子合併，但增加長度限制，以避免字幕過長。

import re
import torch
from tqdm import tqdm
from opencc import OpenCC
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import local

# --- 全域設定 ---
MODEL_NAME = "facebook/nllb-200-1.3B"  # facebook/nllb-200-distilled-1.3B google/madlad400-3b-mt facebook/nllb-200-1.3B
INPUT_VTT = "subtitles-en.vtt"
OUTPUT_SRT = "translated_bilingual_semantic.srt"
# 限制處理的字幕片段數量的參數
### 如果 MAX_SEGMENTS 設為 None（目前的設定），則會處理所有字幕片段。如果設為具體數字（例如 100），則只會處理前 100 個字幕片段。
MAX_SEGMENTS = None
THREADS = 2
# 【新增】字幕最大字元數限制 (英文原文長度)。
# 這是一個可以調整的參數。一般來說，一行字幕的極限是 40-50 個中文字。
# 考慮到雙語，80-100 個英文字元是一個比較合理的上限。
MAX_CHARS_PER_SUBTITLE = 80

# --- 初始化工具 ---
cc = OpenCC("s2twp")  # 簡轉繁（台灣正體）
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,  # 使用半精度
    low_cpu_mem_usage=True,  # 降低CPU記憶體使用
    device_map="auto",  # 自動設備管理
)

# 為每個線程創建獨立的 pipeline 實例以確保線程安全
_thread_ctx = local()


def get_translator():
    """為當前線程獲取或創建一個獨立的翻譯器 pipeline。"""
    if not hasattr(_thread_ctx, "translator"):
        _thread_ctx.translator = pipeline(
            "translation",
            model=model,
            tokenizer=tokenizer,
            src_lang="eng_Latn",  # 來源語言：英文
            tgt_lang="zho_Hant",  # 目標語言：繁體中文
            max_length=1024,  # 增加長度以處理合併後的長句
        )
    return _thread_ctx.translator


# --- 核心功能函數 ---


def parse_vtt(path):
    """解析 VTT 格式的字幕檔。"""
    entries = []
    with open(path, encoding="utf-8") as f:
        content = f.read()

    # VTT 檔案以雙換行符分隔每個字幕塊，先移除 WEBTT 標頭
    content = re.sub(r"WEBVTT.*\n", "", content).strip()
    blocks = re.split(r"\n\n+", content)

    for i, block in enumerate(blocks):
        lines = block.strip().splitlines()
        if not lines:
            continue

        # 處理時間戳行
        if "-->" in lines[0]:
            time_line_index = 0
        elif len(lines) > 1 and "-->" in lines[1]:
            time_line_index = 1
        else:
            continue  # 無效的塊

        start, end = lines[time_line_index].split(" --> ")
        text = " ".join(l.strip() for l in lines[time_line_index + 1 :] if l.strip())

        if text:
            entries.append(
                {"index": str(i + 1), "start": start, "end": end, "text": text}
            )

    return entries[:MAX_SEGMENTS]


def finalize_group(group):
    """輔助函數：將一個分組合併成最終的字幕條目。"""
    if not group:
        return None
    combined_text = " ".join([e["text"] for e in group])
    return {
        "start": group[0]["start"],
        "end": group[-1]["end"],
        "text": combined_text,
        "zh": "",
    }


def group_entries_by_sentence(entries):
    """
    【修改】將字幕片段按完整句子或最大長度進行分組。
    這是解決字幕過長問題的關鍵。
    """
    grouped_entries = []
    current_group = []

    if not entries:
        return []

    for entry in entries:
        # 檢查如果將當前 entry 加入 group，長度是否會超限
        current_text_len = len(" ".join([e["text"] for e in current_group]))
        if (
            current_group
            and current_text_len + len(entry["text"]) > MAX_CHARS_PER_SUBTITLE
        ):
            # 長度超限，強制結束當前分組
            final_entry = finalize_group(current_group)
            if final_entry:
                grouped_entries.append(final_entry)
            current_group = []  # 重置分組

        # 將當前 entry 加入（新的或未滿的）分組
        current_group.append(entry)

        # 檢查是否達到句子結尾
        if entry["text"].strip().endswith((".", "?", "!", "。", "？", "！")):
            final_entry = finalize_group(current_group)
            if final_entry:
                grouped_entries.append(final_entry)
            current_group = []  # 重置分組

    # 處理循環結束後剩餘的最後一組
    if current_group:
        final_entry = finalize_group(current_group)
        if final_entry:
            grouped_entries.append(final_entry)

    return grouped_entries


import ctranslate2

# 初始化 tokenizer 與 CTranslate2 Translator
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
translator = ctranslate2.Translator("./madlad400-ct2", device="cuda")


def translate_entry(entry):
    """使用 CTranslate2 翻譯單一字幕條目。"""
    try:
        # 編碼輸入文本
        tokens = tokenizer.convert_ids_to_tokens(tokenizer(entry["text"])["input_ids"])
        results = translator.translate_batch([tokens], beam_size=1)
        translated_tokens = results[0].hypotheses[0]
        translated_text = tokenizer.convert_tokens_to_string(translated_tokens)

        entry["zh"] = cc.convert(translated_text.strip())
        return entry
    except Exception as e:
        print(f"Error translating entry: {entry['text']}. Error: {e}")
        entry["zh"] = f"[翻譯失敗] {entry['text']}"
        return entry


def translate_all(grouped_entries):
    """使用多線程並行翻譯所有分組後的字幕條目。"""
    results = []
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        # 直接提交分組後的條目
        futures = [executor.submit(translate_entry, entry) for entry in grouped_entries]

        for future in tqdm(
            as_completed(futures), total=len(futures), desc="句子分組翻譯中"
        ):
            results.append(future.result())

    # 保持原始順序
    results.sort(key=lambda e: e["start"])
    return results


def write_srt(entries, path):
    """將處理好的字幕條目寫入 SRT 檔案。"""
    with open(path, "w", encoding="utf-8") as f:
        for i, e in enumerate(entries):
            # SRT 格式要求時間戳中的小數點用逗號
            start = e["start"].replace(".", ",")
            end = e["end"].replace(".", ",")

            # 寫入序號、時間戳、中文翻譯和原始英文
            f.write(f"{i + 1}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{e['zh']}\n")
            f.write(f"{e['text']}\n\n")


# --- 主執行流程 ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Merge and translate VTT subtitles into bilingual SRT."
    )
    parser.add_argument(
        "--input", type=str, default="subtitles-en.vtt", help="Path to input VTT file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="translated_bilingual_semantic.srt",
        help="Path to output SRT file",
    )
    args = parser.parse_args()
    print("1. 開始解析 VTT 檔案...")
    entries = parse_vtt(INPUT_VTT)
    print(f"   解析完成，共 {len(entries)} 條原始字幕片段。")

    print(f"2. 開始按句子或最大長度 ({MAX_CHARS_PER_SUBTITLE}字元) 合併字幕...")
    grouped_entries = group_entries_by_sentence(entries)
    print(f"   合併完成，共形成 {len(grouped_entries)} 條長度適中的字幕進行翻譯。")

    print("3. 開始進行多線程翻譯...")
    translated_entries = translate_all(grouped_entries)

    print(f"4. 開始寫入雙語 SRT 檔案至 {OUTPUT_SRT}...")
    write_srt(translated_entries, OUTPUT_SRT)

    print(f"✅ 全部完成！輸出檔案：{OUTPUT_SRT}")
