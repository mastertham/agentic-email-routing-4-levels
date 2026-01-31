from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Memory:
    """Very small in-memory store (replace with DB/vector store later)."""
    store: Dict[str, Any] = field(default_factory=dict)
    history: List[str] = field(default_factory=list)

    def write(self, key: str, value: Any) -> None:
        self.store[key] = value
        self.history.append(f"WRITE {key}={value!r}")

    def read(self, key: str, default: Any = None) -> Any:
        self.history.append(f"READ {key}")
        return self.store.get(key, default)

    def add_event(self, text: str) -> None:
        self.history.append(text)
