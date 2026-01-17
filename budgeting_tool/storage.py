from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from budgeting_tool.models import Goal, Transaction

DEFAULT_DATA = {
    "currency": "EUR",
    "budgets": {},
    "transactions": [],
    "goals": [],
}


def load_data(path: Path) -> dict:
    if not path.exists():
        return DEFAULT_DATA.copy()
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_data(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def add_transaction(data: dict, transaction: Transaction) -> None:
    entry = asdict(transaction)
    entry["date"] = transaction.date.isoformat()
    entry["type"] = transaction.transaction_type
    entry.pop("transaction_type", None)
    data["transactions"].append(entry)


def add_goal(data: dict, goal: Goal) -> None:
    entry = asdict(goal)
    entry["deadline"] = goal.deadline.isoformat() if goal.deadline else None
    data["goals"].append(entry)


def parse_date(value: str) -> date:
    return date.fromisoformat(value)
