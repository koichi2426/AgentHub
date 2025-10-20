from dataclasses import dataclass


@dataclass(frozen=True)
class ID:
    """シンプルな ID 値オブジェクトラッパー（整数型）"""
    value: int

    def __post_init__(self) -> None:
        if not isinstance(self.value, int):
            raise TypeError(f"ID.value must be int, got {type(self.value).__name__}")
        if self.value < 0:
            raise ValueError("ID.value must be non-negative")

    def __str__(self) -> str:
        return str(self.value)

