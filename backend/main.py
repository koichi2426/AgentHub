from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.router.fastapi import router

# FastAPIインスタンスを作成
app = FastAPI(
    title="AgentHub-Training API",
    description="A FastAPI application for AgentHub-Training.",
    version="0.1.0",
)

# フロントエンドからのアクセスを許可するためのCORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを組み込む
app.include_router(router)


@app.get("/")
def read_root():
    """
    ルートエンドポイント
    """
    return {"message": "Hello from Backend!"}


@app.get("/health")
def health_check():
    """
    ヘルスチェック用エンドポイント
    """
    return {"status": "ok"}