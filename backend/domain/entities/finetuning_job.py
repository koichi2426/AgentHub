import abc
from dataclasses import dataclass
from typing import Optional

from ..value_objects.id import ID
from datetime import datetime


@dataclass
class FinetuningJob:
    """
    ファインチューニングジョブのドメインエンティティ。
    ワーカーの実行に必要なメタデータを含む。
    """
    id: ID
    agent_id: ID
    training_file_path: str   # ★ 必須: ワーカーがファイルを読み込むための共有ストレージパス ★
    status: str               # e.g. 'queued' | 'running' | 'completed' | 'failed'
    model_id: Optional[ID]    # 生成されたモデルのID
    created_at: datetime      # ★ datetime型に変更 ★
    finished_at: Optional[datetime] # ★ datetime型に変更 ★
    error_message: Optional[str] # 失敗時のエラー内容


class FinetuningJobRepository(abc.ABC):
    @abc.abstractmethod
    def create_job(self, job: FinetuningJob) -> FinetuningJob:
        """
        ファインチューニングジョブを作成して返す
        """
        pass

    @abc.abstractmethod
    def find_by_id(self, job_id: "ID") -> Optional[FinetuningJob]:
        """
        ジョブIDからジョブを取得する
        """
        pass
        
    @abc.abstractmethod
    def is_any_running(self) -> bool:
        """
        ★ NEW: status='running' のジョブがDBに存在するか確認する（ワーカー排他制御用）
        """
        pass

    @abc.abstractmethod
    def find_next_queued(self) -> Optional[FinetuningJob]:
        """
        ★ NEW: 最も古い 'queued' 状態のジョブを一つ取得する（ワーカーキュー処理用）
        """
        pass

    @abc.abstractmethod
    def list_by_agent(self, agent_id: "ID") -> list[FinetuningJob]:
        """
        指定エージェントに紐づくジョブ一覧を取得する
        """
        pass

    @abc.abstractmethod
    def update_status(self, job_id: "ID", status: str, **kwargs) -> None:
        """
        ★ 修正: ジョブのステータスとメタデータ（finished_at, model_id, error_messageなど）を更新する
        """
        pass

    @abc.abstractmethod
    def delete(self, job_id: "ID") -> None:
        """
        ジョブを削除する
        """
        pass


def NewFinetuningJob(
    id: int,
    agent_id: int,
    training_file_path: str, # ★ 必須項目の追加 ★
    status: str,
    created_at: datetime,      # ★ datetime型に変更 ★
    finished_at: Optional[datetime], # ★ datetime型に変更 ★
    model_id: Optional[int],
    error_message: Optional[str], # ★ 追加 ★
) -> FinetuningJob:
    """
    FinetuningJobエンティティを生成するファクトリ関数
    """
    return FinetuningJob(
        id=ID(id),
        agent_id=ID(agent_id),
        training_file_path=training_file_path,
        status=status,
        created_at=created_at,
        finished_at=finished_at,
        model_id=ID(model_id) if model_id is not None else None,
        error_message=error_message,
    )