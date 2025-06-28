import asyncio
from fastapi import APIRouter, UploadFile, File
from typing import List
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from fastapi.responses import StreamingResponse
from opencc import OpenCC
import torch

router = APIRouter()

MODEL_NAME = "facebook/nllb-200-1.3B"
MAX_TOKENS = 1024
cc = OpenCC("s2twp")

# 模型初始化
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    device_map="auto",
)
translator = pipeline(
    "translation",
    model=model,
    tokenizer=tokenizer,
    src_lang="eng_Latn",
    tgt_lang="zho_Hant",
    max_length=1024,
)


def parse_srt_from_string(content: str):
    entries = []
    blocks = re.split(r"\n{2,}", content.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) >= 3:
            idx = lines[0].strip()
            time_line = lines[1].strip()
            if "-->" not in time_line:
                continue
            start, end = time_line.split(" --> ")
            text_lines = lines[2:]
            text = " ".join(l.strip() for l in text_lines if l.strip())
            entries.append(
                {
                    "index": idx,
                    "start": start,
                    "end": end,
                    "text": text,
                }
            )
    return entries


def safe_translate(text: str):
    try:
        tokens = tokenizer(text)["input_ids"]
        if len(tokens) > MAX_TOKENS:
            return "[內容過長略過]"
        translated_text = translator(text)[0]["translation_text"]
        return cc.convert(translated_text.strip())
    except Exception:
        return f"[翻譯錯誤] {text}"


def translate_entries(entries: List[dict]):
    results = []
    for i, entry in enumerate(entries):
        zh = safe_translate(entry["text"])
        results.append(
            {
                "index": entry["index"],
                "start": entry["start"],
                "end": entry["end"],
                "text": entry["text"],
                "zh": zh,
            }
        )
    return results


def build_srt_content(entries: List[dict]) -> str:
    srt = ""
    for i, e in enumerate(entries):
        start = e["start"].replace(".", ",")
        end = e["end"].replace(".", ",")
        srt += f"{i+1}\n"
        srt += f"{start} --> {end}\n"
        srt += f"{e['zh']}\n"
        srt += f"{e['text']}\n\n"
    return srt.strip()


@router.post("/translate_srt")
async def translate_srt_file(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8")
    entries = parse_srt_from_string(content)
    translated = translate_entries(entries)
    srt_content = build_srt_content(translated)
    return {"translated_srt": srt_content}


@router.post("/translate_srt_test")
async def translate_srt_filetest(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8")
    entries = parse_srt_from_string(content)

    def to_seconds(time_str):
        hms, ms = time_str.split(",")
        h, m, s = hms.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s) + float(f"0.{ms}")

    limited_entries = []
    for entry in entries:
        if to_seconds(entry["start"]) <= 10:
            limited_entries.append(entry)
        else:
            break

    translated = translate_entries(limited_entries)
    srt_content = build_srt_content(translated)
    return {"translated_srt": srt_content}


@router.post("/translate_srt_stream")
async def translate_srt_stream(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8")
    entries = parse_srt_from_string(content)

    async def generate():
        for i, entry in enumerate(entries):
            zh = safe_translate(entry["text"])
            srt_block = (
                f"{i+1}\n"
                f"{entry['start'].replace('.', ',')} --> {entry['end'].replace('.', ',')}\n"
                f"{zh}\n"
                f"{entry['text']}\n\n"
            )
            yield srt_block
            await asyncio.sleep(0.05)  # 模擬人類輸出節奏（可視需要調整）

    return StreamingResponse(generate(), media_type="text/plain")


@router.get("/ping")
async def ping():
    return {"message": "pong"}
