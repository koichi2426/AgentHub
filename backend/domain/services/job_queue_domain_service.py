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
        
    def enqueue_deployment_job(self, job_id: int, model_path: str) -> None:
        """
        指定されたデプロイメントジョブを非同期キューに投入する。

        Args:
            job_id: データベースに登録されたジョブのID。
            model_path: 訓練モデルが保存されている共有ストレージ上のパス。
        """
        ...
        
    def enqueue_engine_test_job(self, job_id: int, deployment_id: int, test_data_path: str) -> None:
        """
        指定されたエンジンテストジョブを非同期キューに投入する。

        Args:
            job_id: データベースに登録されたジョブのID。
            deployment_id: テスト対象のモデルがデプロイされているインスタンスのID。
            test_data_path: テストに使用するデータファイルが保存されている共有ストレージ上のパス。
        """
        ...