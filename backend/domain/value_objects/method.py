# backend/domain/value_objects/method.py
from dataclasses import dataclass


@dataclass(frozen=True)
class Method:
    """
    デプロイメントが公開する個々のメソッド（機能）を表す値オブジェクト。
    
    例: "generate_summary", "filter_candidates"
    """
    name: str

    def __post_init__(self):
        # 値オブジェクトの責務として、値の検証を行う
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Method name must be a non-empty string.")
        
        # 将来的に、名前に使える文字種のバリデーションなどを追加できる
        # (例: a-z, 0-9, _ のみ許可)

    def __str__(self) -> str:
        return self.name