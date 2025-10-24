from datetime import datetime as PythonDateTime # Python標準のdatetimeライブラリを使用

# ドメイン層の抽象サービスをインポート
from domain.services.system_time_domain_service import SystemTimeDomainService 

class SystemTimeDomainServiceImpl(SystemTimeDomainService):
    """
    SystemTimeDomainService の具体的な実装（インフラ層アダプタ）。
    Pythonの datetime モジュールに依存し、現在時刻のISO文字列を生成する。
    """
    def get_current_time(self) -> str:
        """
        現在のUTC時刻を ISO 8601形式の文字列（str）として返す。
        """
        # Python標準ライブラリを使用して現在時刻を取得し、ISO 8601形式に変換
        return PythonDateTime.utcnow().isoformat()


def NewSystemTimeDomainService() -> SystemTimeDomainService:
    """
    SystemTimeDomainService の新しいインスタンスを生成するファクトリ関数。
    """
    return SystemTimeDomainServiceImpl()