# EchoSub 🗣️🎬
> 即時語音轉字幕 + 多語翻譯｜Whisper + NLLB 離線開源字幕神器

🎯 為什麼存在？
在看 Stanford AI 課、TED 講座、外語影片時，我總遇到「沒有字幕 / 看不懂」的情況。這就是我做 EchoSub 的理由：讓任何一段語音，都能在你眼前變成即時可讀的多語字幕。

🛠️ 技術堆疊
- Whisper (語音辨識)
- NLLB 200 / 600M (多語翻譯)
- Next.js + shadcn UI (字幕顯示)
- Docker / FFmpeg / Ollama (本地部署)

🎥 DEMO
👉 [影片連結] or [點我看動畫](./docs/demo.gif)

📦 一鍵啟動
```bash
git clone echo-sub
cd echo-sub
docker compose up
