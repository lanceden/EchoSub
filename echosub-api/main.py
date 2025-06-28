from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.routes_translate_srt_api import router as translate_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # 或 ["*"] 開發時開放全部
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(translate_router)


@app.get("/")
def health_check():
    return {"status": "ok"}
