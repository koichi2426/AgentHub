import abc
from typing import Protocol

class SystemTimeDomainService(abc.ABC):
    """
    システムの現在時刻を取得するドメインサービスインターフェース。
    ユースケースは具体的な時刻取得ライブラリ（datetime, time）に依存しない。
    """
    @abc.abstractmethod
    def get_current_time(self) -> str:
        """
        現在のシステム時刻を ISO 8601形式の文字列（str）として返す。
        """
        pass