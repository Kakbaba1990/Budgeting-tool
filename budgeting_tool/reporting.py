from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable


def filter_transactions(transactions: Iterable[dict], month: str | None = None) -> list[dict]:
    if not month:
        return list(transactions)
    return [
        transaction
        for transaction in transactions
        if transaction["date"].startswith(month)
    ]


def calculate_totals(transactions: Iterable[dict]) -> dict:
    totals = {"income": 0.0, "expense": 0.0}
    for transaction in transactions:
        transaction_type = transaction["type"]
        totals[transaction_type] += float(transaction["amount"])
    totals["balance"] = totals["income"] - totals["expense"]
    return totals


def category_breakdown(transactions: Iterable[dict], transaction_type: str) -> dict[str, float]:
    breakdown: dict[str, float] = defaultdict(float)
    for transaction in transactions:
        if transaction["type"] != transaction_type:
            continue
        breakdown[transaction["category"]] += float(transaction["amount"])
    return dict(sorted(breakdown.items()))


def budget_status(budgets: dict, expenses: dict[str, float]) -> list[dict]:
    rows = []
    for category, limit in budgets.items():
        spent = expenses.get(category, 0.0)
        remaining = float(limit) - spent
        rows.append(
            {
                "category": category,
                "limit": float(limit),
                "spent": spent,
                "remaining": remaining,
            }
        )
    return sorted(rows, key=lambda row: row["category"].lower())


def format_currency(amount: float, currency: str) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}{currency} {abs(amount):,.2f}"


def parse_month(value: str | None) -> tuple[int, int] | None:
    if not value:
        return None
    year, month = value.split("-")
    return int(year), int(month)


def filter_goals(goals: Iterable[dict], today: date | None = None) -> list[dict]:
    if not today:
        today = date.today()
    sorted_goals = sorted(goals, key=lambda goal: goal["name"].lower())
    for goal in sorted_goals:
        goal["is_overdue"] = bool(goal.get("deadline") and goal["deadline"] < today.isoformat())
    return sorted_goals
