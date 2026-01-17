from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

TransactionType = Literal["income", "expense"]


@dataclass(frozen=True)
class Transaction:
    date: date
    category: str
    amount: float
    transaction_type: TransactionType
    note: str = ""


@dataclass(frozen=True)
class Goal:
    name: str
    target: float
    saved: float
    deadline: date | None = None
    note: str = ""
