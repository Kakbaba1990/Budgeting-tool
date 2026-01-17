from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from budgeting_tool.models import Goal, Transaction
from budgeting_tool.reporting import (
    budget_status,
    calculate_totals,
    category_breakdown,
    filter_goals,
    filter_transactions,
    format_currency,
)
from budgeting_tool.storage import (
    DEFAULT_DATA,
    add_goal,
    add_transaction,
    load_data,
    parse_date,
    save_data,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Uitgebreide budgeting tool")
    parser.add_argument("--data", type=Path, default=Path("budget_data.json"))
    parser.add_argument("--currency", default="EUR")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init", help="Initialiseer een nieuw databestand")

    add_income = subparsers.add_parser("add-income", help="Registreer een inkomstenpost")
    add_income.add_argument("--amount", type=float, required=True)
    add_income.add_argument("--category", required=True)
    add_income.add_argument("--date", type=parse_date, default=date.today())
    add_income.add_argument("--note", default="")

    add_expense = subparsers.add_parser("add-expense", help="Registreer een uitgave")
    add_expense.add_argument("--amount", type=float, required=True)
    add_expense.add_argument("--category", required=True)
    add_expense.add_argument("--date", type=parse_date, default=date.today())
    add_expense.add_argument("--note", default="")

    set_budget = subparsers.add_parser("set-budget", help="Stel een budget in per categorie")
    set_budget.add_argument("--category", required=True)
    set_budget.add_argument("--amount", type=float, required=True)

    list_cmd = subparsers.add_parser("list", help="Toon transacties")
    list_cmd.add_argument("--type", choices=["income", "expense"])
    list_cmd.add_argument("--month", help="Filter op maand (YYYY-MM)")

    summary = subparsers.add_parser("summary", help="Maak een samenvatting")
    summary.add_argument("--month", help="Filter op maand (YYYY-MM)")

    goals = subparsers.add_parser("goals", help="Beheer spaardoelen")
    goals_sub = goals.add_subparsers(dest="goals_command", required=True)
    goals_add = goals_sub.add_parser("add", help="Voeg een spaardoel toe")
    goals_add.add_argument("--name", required=True)
    goals_add.add_argument("--target", type=float, required=True)
    goals_add.add_argument("--saved", type=float, default=0.0)
    goals_add.add_argument("--deadline", type=parse_date)
    goals_add.add_argument("--note", default="")
    goals_sub.add_parser("list", help="Toon spaardoelen")

    export_csv = subparsers.add_parser("export-csv", help="Exporteer transacties naar CSV")
    export_csv.add_argument("--output", type=Path, required=True)

    return parser


def handle_init(data_path: Path, currency: str) -> None:
    data = DEFAULT_DATA.copy()
    data["currency"] = currency
    save_data(data_path, data)
    print(f"Nieuw databestand aangemaakt: {data_path}")


def handle_add_transaction(data_path: Path, currency: str, args: argparse.Namespace, transaction_type: str) -> None:
    data = load_data(data_path)
    if "currency" not in data:
        data["currency"] = currency
    transaction = Transaction(
        date=args.date,
        category=args.category,
        amount=args.amount,
        transaction_type=transaction_type,
        note=args.note,
    )
    add_transaction(data, transaction)
    save_data(data_path, data)
    print(f"{transaction_type.title()} toegevoegd: {format_currency(args.amount, data['currency'])}")


def handle_set_budget(data_path: Path, args: argparse.Namespace) -> None:
    data = load_data(data_path)
    data.setdefault("budgets", {})[args.category] = args.amount
    save_data(data_path, data)
    print(f"Budget ingesteld voor {args.category}: {args.amount}")


def handle_list(data_path: Path, args: argparse.Namespace) -> None:
    data = load_data(data_path)
    transactions = filter_transactions(data.get("transactions", []), args.month)
    if args.type:
        transactions = [item for item in transactions if item["type"] == args.type]

    if not transactions:
        print("Geen transacties gevonden.")
        return

    for item in transactions:
        print(
            f"{item['date']} | {item['type'].upper():7} | {item['category']:<15} | "
            f"{format_currency(float(item['amount']), data.get('currency', 'EUR'))} | {item.get('note', '')}"
        )


def handle_summary(data_path: Path, args: argparse.Namespace) -> None:
    data = load_data(data_path)
    transactions = filter_transactions(data.get("transactions", []), args.month)
    totals = calculate_totals(transactions)
    currency = data.get("currency", "EUR")

    print("Samenvatting")
    if args.month:
        print(f"Maand: {args.month}")
    print(f"Inkomsten: {format_currency(totals['income'], currency)}")
    print(f"Uitgaven: {format_currency(totals['expense'], currency)}")
    print(f"Balans: {format_currency(totals['balance'], currency)}")

    expenses_by_category = category_breakdown(transactions, "expense")
    if expenses_by_category:
        print("\nUitgaven per categorie")
        for category, amount in expenses_by_category.items():
            print(f"- {category}: {format_currency(amount, currency)}")

    budgets = data.get("budgets", {})
    if budgets:
        print("\nBudgetstatus")
        for row in budget_status(budgets, expenses_by_category):
            print(
                f"- {row['category']}: {format_currency(row['spent'], currency)} "
                f"van {format_currency(row['limit'], currency)} "
                f"(over: {format_currency(row['remaining'], currency)})"
            )


def handle_goals_add(data_path: Path, args: argparse.Namespace) -> None:
    data = load_data(data_path)
    goal = Goal(
        name=args.name,
        target=args.target,
        saved=args.saved,
        deadline=args.deadline,
        note=args.note,
    )
    add_goal(data, goal)
    save_data(data_path, data)
    print(f"Spaardoel toegevoegd: {goal.name}")


def handle_goals_list(data_path: Path) -> None:
    data = load_data(data_path)
    goals = filter_goals(data.get("goals", []))
    if not goals:
        print("Geen spaardoelen gevonden.")
        return

    currency = data.get("currency", "EUR")
    for goal in goals:
        deadline = goal.get("deadline") or "geen"
        status = "(verlopen)" if goal.get("is_overdue") else ""
        print(
            f"{goal['name']} | Doel: {format_currency(float(goal['target']), currency)} | "
            f"Gespaard: {format_currency(float(goal['saved']), currency)} | Deadline: {deadline} {status}"
        )
        if goal.get("note"):
            print(f"  Notitie: {goal['note']}")


def handle_export_csv(data_path: Path, output: Path) -> None:
    data = load_data(data_path)
    transactions = data.get("transactions", [])
    if not transactions:
        print("Geen transacties om te exporteren.")
        return

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "type", "category", "amount", "note"])
        writer.writeheader()
        writer.writerows(transactions)

    print(f"Transacties geëxporteerd naar {output}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "init":
        handle_init(args.data, args.currency)
        return
    if args.command == "add-income":
        handle_add_transaction(args.data, args.currency, args, "income")
        return
    if args.command == "add-expense":
        handle_add_transaction(args.data, args.currency, args, "expense")
        return
    if args.command == "set-budget":
        handle_set_budget(args.data, args)
        return
    if args.command == "list":
        handle_list(args.data, args)
        return
    if args.command == "summary":
        handle_summary(args.data, args)
        return
    if args.command == "goals":
        if args.goals_command == "add":
            handle_goals_add(args.data, args)
        else:
            handle_goals_list(args.data)
        return
    if args.command == "export-csv":
        handle_export_csv(args.data, args.output)
        return


if __name__ == "__main__":
    main()
