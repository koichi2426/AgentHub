# backend/domain/services/deployment_test_domain_service.py

import abc
from typing import Protocol, List, Dict, Any

# ドメイン層の依存関係
from domain.value_objects.file_data import UploadedFileStream 
from domain.value_objects.deployment_test_result import DeploymentTestResult 

    
# ======================================
# DeploymentTestDomainService (プロトコル定義)
# ======================================
class DeploymentTestDomainService(Protocol):
    """
    デプロイされた推論エンジンに対するテスト実行ロジックをカプセル化するドメインサービスインターフェース。
    """
    
    @abc.abstractmethod
    async def run_batch_inference_test(
        self, 
        test_file: UploadedFileStream,
        endpoint_url: str,
    ) -> DeploymentTestResult: 
        """
        テストデータファイルの内容を解析し、外部エンドポイントに対し
        並列でリクエストを発行し、最終的な評価結果V.O.を返す。
        
        Args:
            test_file: テストデータファイル。
            endpoint_url: 推論を行うデプロイメントの完全なエンドポイントURL。
            
        Returns:
            DeploymentTestResult: テスト実行の最終結果を含むV.O.。
        """
        ...