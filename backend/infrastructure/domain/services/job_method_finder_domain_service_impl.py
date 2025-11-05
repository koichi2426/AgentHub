import requests
import json
import os  # ★ 環境変数を読み込むためにインポート
from typing import List, Optional
from urllib.parse import urljoin

# ドメイン（インターフェースと値オブジェクト）
from domain.services.job_method_finder_domain_service import JobMethodFinderDomainService
from domain.value_objects.id import ID
from domain.value_objects.method import Method

# 外部ライブラリ 'requests' が必要です
# (pip install requests)


class JobMethodFinderDomainServiceImpl(JobMethodFinderDomainService):
    """
    JobMethodFinderDomainService のインフラ層における実装クラス。
    
    責務：
    C++で起動している agenthub-engine の /methods エンドポイントに
    HTTPリクエストを送信し、メソッドリストを取得する。
    
    (DBリポジトリではなく、HTTPクライアントとして動作します)
    """

    def __init__(self, timeout: int = 5):
        """
        Args:
            timeout (int): HTTPリクエストのタイムアウト秒
        """
        # ★ 引数から base_url を削除し、環境変数から読み込む
        base_url = os.environ.get("AGENTHUB_ENGINE_BASE_URL")
        
        # ★ 環境変数が設定されていない場合は、エラーを発生させて起動を停止
        if not base_url:
            raise ValueError("AGENTHUB_ENGINE_BASE_URL environment variable is not set.")
            
        if not base_url.endswith('/'):
            base_url += '/'
            
        self.base_url = base_url
        self.timeout = timeout
        
        print(f"JobMethodFinder service initialized. Target base URL: {self.base_url}") # 起動ログ

    def find_methods_by_job_id(self, job_id: ID) -> List[Method]:
        """
        ジョブIDに紐づくメソッドのリストを返す。
        """
        
        # 1. "job45" のようなパスを作成
        job_path = f"job{job_id.value}/"
        
        # 2. ベースURLと安全に結合 -> "http://.../job45/methods"
        endpoint_path = urljoin(job_path, "methods")
        full_url = urljoin(self.base_url, endpoint_path)

        try:
            # 3. C++ サーバーに GET リクエストを送信
            response = requests.get(full_url, timeout=self.timeout)
            
            # 4. HTTPステータスコードチェック
            response.raise_for_status() # 200番台以外なら例外を発生させる
            
            # 5. JSONレスポンスをパース
            data = response.json()
            
            # 6. "methods" キーから文字列のリストを取得
            method_names: List[str] = data.get("methods", [])
            
            # 7. 文字列リストを Method 値オブジェクトのリストに変換
            method_vos = [Method(name=name) for name in method_names if name]
            return method_vos

        except requests.exceptions.RequestException as e:
            # タイムアウト、接続エラー、404/500エラーなど
            # TODO: 適切なロギング
            print(f"[ERROR] JobMethodFinder failed to fetch {full_url}: {e}")
            return [] # インターフェースの規約通り、エラー時は空リストを返す
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            # レスポンスが期待したJSON形式でない場合
            # TODO: 適切なロギング
            print(f"[ERROR] JobMethodFinder failed to parse JSON from {full_url}: {e}")
            return []