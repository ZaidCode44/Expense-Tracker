"""
Expense Tracker — Project 2
=============================

A state-preserving, terminal-based expense tracker built around three
explicitly separated concerns (IPO Architecture):

    INPUT    -> read_raw_input()
    PROCESS  -> parse_amount(), accumulate()
    OUTPUT   -> display_*() functions

Design principles applied:
    - Poka-Yoke (defensive coding): every numeric conversion is wrapped in
      try/except ValueError, so malformed input can never crash the session.
    - Accumulator pattern: `total` and `transactions` are initialized ONCE,
      outside the while loop, so state persists across every iteration
      instead of resetting each time through the loop ("state amnesia").
    - Sentinel-controlled loop: typing quit/exit/stop at any prompt ends the
      session gracefully and prints a final summary.

Run it with:
    python expense_tracker.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

# --- Configuration -----------------------------------------------------

SENTINELS = {"quit", "exit", "stop"}


# --- Data model ----------------------------------------------------------

@dataclass
class Transaction:
    """A single recorded expense."""

    description: str
    amount: float
    timestamp: datetime = field(default_factory=datetime.now)


# --- INPUT layer ---------------------------------------------------------
# Responsible only for collecting raw strings from the user. It knows
# nothing about validation, math, or formatting.

def read_raw_input(prompt: str) -> str:
    """Read a single line of raw text from the terminal, whitespace-trimmed."""
    return input(prompt).strip()


def is_sentinel(value: str) -> bool:
    """True if the user typed a stop word ('quit', 'exit', or 'stop')."""
    return value.lower() in SENTINELS


# --- PROCESS layer ---------------------------------------------------------
# Pure(-ish) functions: validation, parsing, and the running total. No
# print() statements live here — this logic could be unit-tested or reused
# in a GUI/web version without changing a single line.

def parse_amount(raw_amount: str) -> float:
    """
    Convert a raw string into a validated, positive expense amount.

    Raises:
        ValueError: if the input isn't a number, or isn't positive.
                    float() itself raises ValueError for non-numeric text
                    (e.g. "abc"), which is caught by the caller; the extra
                    check below adds a domain-specific rule (no negative or
                    zero-dollar expenses) on top of that.
    """
    amount = float(raw_amount)  # raises ValueError on non-numeric input
    if amount <= 0:
        raise ValueError("Amount must be a positive number.")
    return round(amount, 2)


def accumulate(total: float, amount: float) -> float:
    """Return the new running total after adding one transaction's amount."""
    return round(total + amount, 2)


def prompt_for_amount(index: int) -> Optional[float]:
    """
    Repeatedly prompt for a valid amount until one is given, WITHOUT
    re-asking for the description. This keeps a bad amount entry isolated
    to just this one field, instead of discarding the description the user
    already typed.

    Returns:
        The validated amount, or None if the user typed a sentinel here.
    """
    while True:
        raw_amount = read_raw_input(f"[{index}] Amount ($): ")
        if is_sentinel(raw_amount):
            return None
        try:
            return parse_amount(raw_amount)
        except ValueError as exc:
            display_error(str(exc))
            # loop again, re-prompting ONLY for the amount


# --- OUTPUT layer ---------------------------------------------------------
# Every print() call lives here, deliberately separated from the process
# layer above, so display formatting can change freely without touching
# any business logic.

def display_welcome() -> None:
    stop_words = ", ".join(f"'{word}'" for word in sorted(SENTINELS))
    print("=" * 48)
    print("        EXPENSE TRACKER — TERMINAL SESSION")
    print("=" * 48)
    print("Enter a description and amount for each expense.")
    print(f"Type {stop_words} at any prompt to finish.\n")


def display_confirmation(transaction: Transaction, total: float, count: int) -> None:
    print(
        f"  ✓ [{count:>2}] {transaction.description:<25} "
        f"${transaction.amount:>8.2f}   running total: ${total:>9.2f}\n"
    )


def display_error(message: str) -> None:
    print(f"  ✗ Invalid input: {message} Please try again.\n")


def display_summary(transactions: List[Transaction], total: float) -> None:
    print("\n" + "=" * 48)
    print("                SESSION SUMMARY")
    print("=" * 48)

    if not transactions:
        print("No transactions were recorded this session.")
        print("=" * 48)
        return

    for i, t in enumerate(transactions, start=1):
        stamp = t.timestamp.strftime("%H:%M:%S")
        print(f"  {i:>2}. [{stamp}] {t.description:<25} ${t.amount:>8.2f}")

    average = round(total / len(transactions), 2)
    print("-" * 48)
    print(f"  Transactions recorded : {len(transactions)}")
    print(f"  Total spent           : ${total:,.2f}")
    print(f"  Average per expense   : ${average:,.2f}")
    print("=" * 48)
    print("Session ended. Goodbye!")


# --- Orchestration ---------------------------------------------------------

def run_session() -> None:
    """
    Main execution loop.

    `total` and `transactions` are the accumulator state: both are created
    ONCE here, before the loop begins, and are only ever updated (never
    reset) on each successful iteration — this is what allows the running
    total to persist correctly across any number of transactions.
    """
    display_welcome()

    total: float = 0.0
    transactions: List[Transaction] = []

    while True:
        description = read_raw_input(f"[{len(transactions) + 1}] Description: ")
        if is_sentinel(description):
            break

        amount = prompt_for_amount(len(transactions) + 1)
        if amount is None:  # user typed a sentinel while entering the amount
            break

        total = accumulate(total, amount)
        transaction = Transaction(description=description or "Unlabeled expense", amount=amount)
        transactions.append(transaction)
        display_confirmation(transaction, total, len(transactions))

    display_summary(transactions, total)


if __name__ == "__main__":
    try:
        run_session()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C / Ctrl+D also exits gracefully rather than dumping a traceback.
        print("\n\nSession interrupted. Goodbye!")
