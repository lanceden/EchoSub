```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## API 說明

### 取得前 30 秒字幕
`GET /api/subtitles?youtube_url=https://www.youtube.com/watch?v=XXXX`

### 翻譯字幕
`POST /api/translate`
```json
[
  { "start": 0.0, "duration": 3.2, "text": "Hello world" }
]
```
### 回傳
```
[
  { "start": 0.0, "duration": 3.2, "en": "Hello world", "zh": "（翻譯）Hello world" }
]
```
