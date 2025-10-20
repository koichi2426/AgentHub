from dataclasses import dataclass
import re
from typing import Optional


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        if not EMAIL_RE.match(self.value):
            raise ValueError(f"Invalid email: {self.value}")

    def __str__(self) -> str:
        return self.value
