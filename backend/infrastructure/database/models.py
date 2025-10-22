# backend/infrastructure/database/models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
from typing import Optional
from datetime import datetime

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

    # Agent モデルとのリレーションシップを定義 (オプション)
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

    # User モデルへのリレーションシップを定義 (オプション)
    user = relationship("User", back_populates="agents")
    
    # FinetuningJob モデルとのリレーションシップを定義 (オプション)
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
    
    # ドメインモデルの `model_id: Optional[ID]` に対応
    model_id = Column(String(255), nullable=True)
    
    # ドメインモデルの `created_at: datetime` に対応
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow) # ★ datetime.utcnow が正しく参照される ★
    
    # ドメインモデルの `finished_at: Optional[datetime]` に対応
    finished_at = Column(DateTime, nullable=True)

    # ドメインモデルの `error_message: Optional[str]` に対応
    error_message = Column(Text, nullable=True)
    
    # Agent モデルへのリレーションシップを定義 (オプション)
    agent = relationship("Agent", back_populates="finetuning_jobs")