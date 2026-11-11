from __future__ import annotations

import tempfile
from pathlib import Path

from ..hledger import check_journal
from ..journal import (
    JournalError,
    append_price,
    append_transaction,
    delete_transaction,
    preview_delete,
    preview_replace,
    replace_transaction,
    safe_append,
)


def _dry_run_validate(journal_path: str, new_content: str, success_message: str) -> str:
    """Validate new_content in a uniquely-named temp file; never touches the journal."""
    parent = Path(journal_path).parent
    fd, tmp_name = tempfile.mkstemp(prefix=".hledger_mcp_dry_run_", suffix=".journal", dir=parent)
    try:
        with open(fd, "w", encoding="utf-8") as f:
            f.write(new_content)
        check_journal(tmp_name)
        return success_message
    except Exception as exc:
        raise JournalError(f"Dry run failed: {exc}") from exc
    finally:
        Path(tmp_name).unlink(missing_ok=True)


def tool_add_transaction(
    journal_path: str,
    transaction: str,
    dry_run: bool = False,
) -> str:
    """Add a new transaction to the journal.

    The transaction must be valid hledger syntax, e.g.:

    2026-07-15 Grocery shopping
        expenses:food:groceries    25.50 €
        assets:bank:checking

    Use dry_run=True to validate without modifying the file.
    """
    txn = transaction.strip()
    if not txn:
        raise JournalError("Transaction text cannot be empty")

    if dry_run:
        content = Path(journal_path).read_text(encoding="utf-8")
        return _dry_run_validate(
            journal_path, content + "\n" + txn + "\n", "Dry run successful: transaction is valid."
        )

    append_transaction(Path(journal_path), txn)
    return "Transaction added successfully."


def tool_edit_transaction(
    journal_path: str,
    search_text: str,
    new_transaction: str,
    dry_run: bool = False,
) -> str:
    """Edit an existing transaction in the journal.

    search_text must uniquely identify the transaction (a date, a description, or an amount).
    new_transaction is the complete replacement transaction text.

    Use dry_run=True to validate without modifying the file.
    """
    if not search_text.strip():
        raise JournalError("Search text cannot be empty")
    if not new_transaction.strip():
        raise JournalError("New transaction text cannot be empty")

    if dry_run:
        # Simulate the exact block replacement applied by replace_transaction.
        preview = preview_replace(Path(journal_path), search_text, new_transaction)
        if preview is None:
            raise JournalError(f"Search text not found in journal: {search_text}")
        _, new_content = preview
        return _dry_run_validate(journal_path, new_content, "Dry run successful: replacement is valid.")

    result = replace_transaction(Path(journal_path), search_text, new_transaction)
    if result == 0:
        raise JournalError(f"Search text not found in journal: {search_text}")
    return "Transaction edited successfully."


def tool_delete_transaction(
    journal_path: str,
    search_text: str,
    dry_run: bool = False,
) -> str:
    """Delete a transaction from the journal.

    search_text must uniquely identify the transaction.
    The first matching transaction is removed.

    Use dry_run=True to validate without modifying the file.
    """
    if not search_text.strip():
        raise JournalError("Search text cannot be empty")

    if dry_run:
        # Validate the journal as if the transaction were actually removed.
        preview = preview_delete(Path(journal_path), search_text)
        if preview is None:
            raise JournalError(f"Search text not found in journal: {search_text}")
        _, new_content = preview
        return _dry_run_validate(
            journal_path, new_content, "Dry run successful: transaction can be safely removed."
        )

    result = delete_transaction(Path(journal_path), search_text)
    if result == 0:
        raise JournalError(f"Search text not found in journal: {search_text}")
    return "Transaction deleted successfully."


def tool_add_price(
    journal_path: str,
    date: str,
    commodity: str,
    price: str,
    dry_run: bool = False,
) -> str:
    """Add a P (price) directive to the journal.

    Example: date="2026-07-15", commodity="EUR", price="1.08 USD"

    Use dry_run=True to validate without modifying the file.
    """
    if not date.strip():
        raise JournalError("Date cannot be empty")
    if not commodity.strip():
        raise JournalError("Commodity cannot be empty")
    if not price.strip():
        raise JournalError("Price cannot be empty")

    price_line = f"P {date} {commodity} {price}"

    if dry_run:
        content = Path(journal_path).read_text(encoding="utf-8") + "\n" + price_line + "\n"
        return _dry_run_validate(journal_path, content, "Dry run successful: price directive is valid.")

    append_price(Path(journal_path), date, commodity, price)
    return "Price directive added successfully."


def tool_add_account(
    journal_path: str,
    account_name: str,
    dry_run: bool = False,
) -> str:
    """Add an account directive to the journal.

    Example: account_name="assets:investments:gold"

    Use dry_run=True to validate without modifying the file.
    """
    if not account_name.strip():
        raise JournalError("Account name cannot be empty")

    directive = f"account {account_name}"

    if dry_run:
        content = Path(journal_path).read_text(encoding="utf-8") + "\n" + directive + "\n"
        return _dry_run_validate(journal_path, content, "Dry run successful: account directive is valid.")

    safe_append(Path(journal_path), directive + "\n", Path(journal_path))
    return "Account directive added successfully."


def tool_check(journal_path: str) -> str:
    """Validate the journal with hledger check. Returns validation status."""
    try:
        check_journal(journal_path)
        return "Journal is valid."
    except Exception as exc:
        return f"Journal validation failed: {exc}"
