# EchoSub 🗣️🎬  
> 即時語音轉字幕 + 雙語翻譯｜Whisper + NLLB 離線字幕神器

🎯 **為什麼存在？**  
在看 Stanford AI 課、TED 講座、國外影片時，我總遇到「沒有字幕 / 看不懂」的情況。這就是我做 EchoSub 的理由：讓任何一段語音，都能在你眼前變成即時可讀的雙語字幕。

---

## ✨ 功能亮點

- 🎙 Whisper 語音辨識：支援本地推理與多語口音
- 🌍 NLLB 翻譯：支援 200+ 種語言，整合 CTranslate2 提升推理效能
- 💬 雙語字幕：中英文並排，對齊時間軸，自動分段
- 🧠 智慧字幕處理邏輯：
  - 按句子切割並合併片段
  - 自訂最大長度避免字幕過長
  - 多線程翻譯與錯誤處理
- 📦 支援 .vtt → 雙語 .srt 字幕產出

---

## 📂 專案架構

```
/echo-sub/
├── frontend/        # Next.js + shadcn UI 字幕播放器 (規劃中)
├── backend/         # Whisper / NLLB API 實作
├── scripts/
│   └── merge_vtt_to_bilingual_srt.py   # 雙語字幕生成器（已完成 ✅）
├── models/          # 模型權重 (faster-whisper / NLLB / CTranslate2)
├── public/          # 測試影片與字幕範例
└── README.md
```

---

## 📽️ DEMO (即將提供)
🎬【播放影片 → 字幕同步出現】的短影片將上線，敬請期待！

---

## ⚙️ 使用方式（字幕轉換工具）

1. 安裝 Python 套件：
```bash
pip install torch transformers ctranslate2 opencc-python-reimplemented
```

2. 執行字幕合併與翻譯：
```bash
python scripts/merge_vtt_to_bilingual_srt.py
```

3. 預設會讀取 `subtitles-en.vtt` 並輸出為 `translated_bilingual_semantic.srt`

---

## 🔬 技術細節｜merge_vtt_to_bilingual_srt.py

> 自動將原始英文字幕（.vtt）轉成「語意完整、時間對齊」的中英雙語 .srt 字幕檔。

| 功能模組 | 說明 |
|----------|------|
| 📌 字幕合併 | 依據句尾標點與最大長度限制，自動將連續片段合併 |
| 🧠 翻譯效能 | 採用 CTranslate2 + 多執行緒加速，支援 GPU |
| 🈳 字體排版 | 雙語字幕採上下排列，更適合觀看影片時閱讀 |
| 🔁 語言轉換 | 使用 OpenCC 進行簡轉繁，預設為台灣用語 |

---

## 🧱 Roadmap

- [x] 雙語字幕合併翻譯模組
- [ ] 即時語音擷取（Streaming / FFmpeg）
- [ ] Next.js 字幕播放器 UI
- [ ] 語言自動偵測與切換 (fastText / CLD3)
- [ ] OBS 插件整合 / 瀏覽器外掛

---

## 👀 適合誰用？

- 想看國外影片卻沒有字幕的人
- AI 工程師 / 學習者觀看英文技術內容卻無法即時理解
- 教學影片創作者需要快速生成雙語字幕
- 有語言障礙需求的族群（聽力弱、移民學生等）

---

## 🤝 加入貢獻！

你可以幫忙：

- 🌍 加入更多語言翻譯模型（如日 → 英）
- 🚀 加速處理流程（支援 streaming、分段 queue）
- 🧪 改進字幕樣式與排版（多人字幕樣式）

---

EchoSub 讓世界上所有語言的聲音，都能成為你眼前的字幕。


