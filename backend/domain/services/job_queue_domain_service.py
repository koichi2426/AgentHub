from typing import Protocol

class JobQueueDomainService(Protocol):
    """
    長時間実行されるジョブを非同期実行キューに投入するドメインサービスインターフェース。
    具体的なキュー実装はインフラ層に委譲される。
    """
    def enqueue_finetuning_job(self, job_id: int, file_path: str) -> None:
        """
        指定されたファインチューニングジョブを非同期キューに投入する。

        Args:
            job_id: データベースに登録されたジョブのID。
            file_path: トレーニングデータが保存されている共有ストレージ上のパス。
        """
        ...