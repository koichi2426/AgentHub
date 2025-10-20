# backend/infrastructure/database/models.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

# 全モデル共通の親クラス
Base = declarative_base()

# --- User テーブル定義 ---
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
    # (アバターは無い場合もあるため nullable=True を推奨)
    avatar_url = Column(String(255), nullable=True)
    
    # ドメインモデルの `password_hash: str` に対応
    password_hash = Column(String(255), nullable=False)