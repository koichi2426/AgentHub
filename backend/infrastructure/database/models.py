import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, BigInteger
from sqlalchemy.dialects import mysql # JSON 型のインポート用
from sqlalchemy.orm import declarative_base, relationship
from typing import Optional

# 全モデル共通の親クラス
Base = declarative_base()

# ----------------- User テーブル定義 -----------------
class User(Base):
    __tablename__ = "users"

    # ドメインモデルの `id: ID` (int) に対応
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # ドメインモデルの `username: str` に対応
    username = Column(String(50), nullable=False, unique=True)
    
    # ドメインモデルの `name: str` に対応
    name = Column(String(100), nullable=False)
    
    # ドメインモデルの `email: Email` (str) に対応
    email = Column(String(255), nullable=False, unique=True)
    
    # ドメインモデルの `avatar_url: str` に対応
    avatar_url = Column(String(255), nullable=True)
    
    # ドメインモデルの `password_hash: str` に対応
    password_hash = Column(String(255), nullable=False)

    # Agent モデルとのリレーションシップを定義
    agents = relationship("Agent", back_populates="user")

# ----------------- Agent テーブル定義 -----------------
class Agent(Base):
    __tablename__ = "agents"

    # ドメインモデルの `id: ID` (int) に対応
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ドメインモデルの `user_id: ID` (int) に対応
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # ドメインモデルの `owner: str` に対応
    owner = Column(String(255), nullable=False)

    # ドメインモデルの `name: str` に対応
    name = Column(String(255), nullable=False)

    # ドメインモデルの `description: Optional[str]` に対応
    description = Column(String(1000), nullable=True)

    # User モデルへのリレーションシップを定義
    user = relationship("User", back_populates="agents")
    
    # FinetuningJob モデルとのリレーションシップを定義
    finetuning_jobs = relationship("FinetuningJob", back_populates="agent")


# ----------------- FinetuningJob テーブル定義 -----------------
class FinetuningJob(Base):
    __tablename__ = "finetuning_jobs"

    # ドメインモデルの `id: ID` (int) に対応
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ドメインモデルの `agent_id: ID` (int) に対応
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)

    # ドメインモデルの `training_file_path: str` に対応
    training_file_path = Column(String(512), nullable=False)
    
    # ドメインモデルの `status: str` に対応
    status = Column(String(50), nullable=False, index=True)
    
    # ★ model_id は削除 ★
    
    # ドメインモデルの `created_at: datetime` に対応
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow) 
    
    # ドメインモデルの `finished_at: Optional[datetime]` に対応
    finished_at = Column(DateTime, nullable=True)

    # ドメインモデルの `error_message: Optional[str]` に対応
    error_message = Column(Text, nullable=True)
    
    # Agent モデルへのリレーションシップを定義
    agent = relationship("Agent", back_populates="finetuning_jobs")


# ----------------- WeightVisualization テーブル定義 (新規追加) -----------------
class WeightVisualization(Base):
    """
    ファインチューニングジョブの結果として生成された、重み変化の可視化データ。
    """
    __tablename__ = "weight_visualizations"

    # job_id は主キーであり、FinetuningJob への外部キーでもある
    job_id = Column(Integer, ForeignKey("finetuning_jobs.id", ondelete="CASCADE"), primary_key=True)

    # layers_data はネストされた視覚化情報（JSON文字列）を格納する
    # MySQL 5.7+ または MariaDB 10.2+ では JSON 型が推奨される
    layers_data = Column(mysql.JSON, nullable=False)

    # FinetuningJob モデルへのリレーションシップを定義 (オプション)
    job = relationship("FinetuningJob", backref="visualization", uselist=False)
