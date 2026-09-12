# Expense Tracker

A production-grade, state-preserving terminal application for tracking
expenses in real time — built to demonstrate clean **IPO architecture**,
**defensive coding (Poka-Yoke)**, and the **accumulator pattern** in Python,
with zero external dependencies.

```
================================================
        EXPENSE TRACKER — TERMINAL SESSION
================================================
Enter a description and amount for each expense.
Type 'exit', 'quit', 'stop' at any prompt to finish.

[1] Description: Coffee
[1] Amount ($): 4.50
  ✓ [ 1] Coffee                    $    4.50   running total: $     4.50

[2] Description: Groceries
[2] Amount ($): abc
  ✗ Invalid input: could not convert string to float: 'abc' Please try again.

[2] Amount ($): 62.30
  ✓ [ 2] Groceries                 $   62.30   running total: $    66.80
```

## Features

- Continuous transaction entry via a real-time input loop
- Graceful exit at any point using a sentinel word (`quit`, `exit`, or `stop`)
- Full input validation — non-numeric and non-positive amounts are rejected
  and re-prompted without crashing or losing prior data
- A running total and itemized final summary (count, total, average)
- No external dependencies to run the app itself — pure Python standard library

## Architecture

The code is organized around three explicitly separated concerns (**Input →
Process → Output**), so each layer can be read, tested, and changed
independently:

| Layer | Functions | Responsibility |
|---|---|---|
| **Input** | `read_raw_input()`, `is_sentinel()` | Collect raw strings only — no validation, no math |
| **Process** | `parse_amount()`, `accumulate()`, `prompt_for_amount()` | Validation and the running total — no `print()` calls anywhere in this layer |
| **Output** | `display_welcome()`, `display_confirmation()`, `display_error()`, `display_summary()` | All terminal formatting, decoupled from the logic that produces the numbers |

This separation is what makes the process layer unit-testable in isolation
(see `tests/`) without mocking `input()`/`print()` at all.

### Key design decisions

- **Accumulator pattern**: `total` and `transactions` are initialized once,
  *outside* the main loop. Every iteration updates them in place — nothing
  is ever reset mid-session, which is what allows the running total to
  persist correctly across any number of entries.
- **Defensive coding (Poka-Yoke)**: `parse_amount()` raises `ValueError` for
  both non-numeric input (via Python's own `float()`) and non-positive
  amounts (a domain rule added on top). The caller catches `ValueError`
  specifically and re-prompts — it never lets a bad entry propagate into a
  crash or corrupt the accumulated state.
- **Isolated retry on bad input**: if the *amount* fails validation, only
  the amount prompt repeats — the description the user already typed is
  preserved, so a typo in one field never forces re-entering the other.

## Requirements

- Python 3.9 or newer (no external packages needed to run the app)

## Installation

```bash
git clone https://github.com/<your-username>/expense-tracker.git
cd expense-tracker
```

No dependency installation is required to run the app itself.

## Usage

```bash
python expense_tracker.py
```

You'll be prompted for a description and amount, repeatedly. Type `quit`,
`exit`, or `stop` at either prompt to end the session and see your summary.

## Running the tests

The process layer (`parse_amount`, `accumulate`, `is_sentinel`) is covered
by a pytest suite with 23 test cases.

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

pytest -v
```

Type checking (the codebase passes `mypy --strict` cleanly):

```bash
mypy expense_tracker.py --strict
```

## Project structure

```
expense-tracker/
├── expense_tracker.py       # the application (single file, stdlib only)
├── tests/
│   └── test_expense_tracker.py
├── requirements-dev.txt     # pytest + mypy, for contributors/CI only
├── LICENSE
└── README.md
```

## Possible extensions

Ideas for taking this further (not implemented, to keep the core example
focused):
- Persist transactions to a CSV/JSON file or SQLite database between runs
- Add expense categories and per-category subtotals
- Add a budget limit with a warning when exceeded
- Export the session summary to a file

## License

MIT — see [LICENSE](LICENSE).
