from fastapi import FastAPI

# FastAPIインスタンスを作成
app = FastAPI(
    title="AgentHub-Training API",
    description="A FastAPI application for AgentHub-Training.",
    version="0.1.0",
)

@app.get("/")
def read_root():
    """
    ルートエンドポイント
    """
    return {"message": "Welcome to AgentHub-Training API"}

@app.get("/health")
def health_check():
    """
    ヘルスチェック用エンドポイント
    """
    return {"status": "ok"}