"""Tests for the write/validate tools in hledger_mcp.tools.mutations."""

from __future__ import annotations

from pathlib import Path

import pytest

from hledger_mcp.journal import JournalError
from hledger_mcp.tools.mutations import (
    tool_add_account,
    tool_add_price,
    tool_add_transaction,
    tool_check,
    tool_delete_transaction,
    tool_edit_transaction,
)
from conftest import UNBALANCED_TXN, VALID_TXN


def test_add_transaction(journal_path: Path):
    assert tool_add_transaction(str(journal_path), VALID_TXN) == "Transaction added successfully."
    assert "Bookshop" in journal_path.read_text(encoding="utf-8")


def test_add_transaction_rejects_empty(journal_path: Path):
    with pytest.raises(JournalError, match="cannot be empty"):
        tool_add_transaction(str(journal_path), "   ")


def test_add_transaction_dry_run_valid_leaves_file_untouched(journal_path: Path):
    before = journal_path.read_text(encoding="utf-8")
    result = tool_add_transaction(str(journal_path), VALID_TXN, dry_run=True)
    assert "successful" in result
    assert journal_path.read_text(encoding="utf-8") == before


def test_add_transaction_dry_run_invalid(journal_path: Path):
    before = journal_path.read_text(encoding="utf-8")
    with pytest.raises(JournalError, match="Dry run failed"):
        tool_add_transaction(str(journal_path), UNBALANCED_TXN, dry_run=True)
    assert journal_path.read_text(encoding="utf-8") == before


def test_edit_transaction_dry_run_validates_replacement(journal_path: Path):
    """dry_run must validate the replacement block, not a naive string swap."""
    before = journal_path.read_text(encoding="utf-8")
    result = tool_edit_transaction(str(journal_path), "Esselunga", VALID_TXN, dry_run=True)
    assert "successful" in result
    assert journal_path.read_text(encoding="utf-8") == before


def test_edit_transaction_dry_run_rejects_unbalanced(journal_path: Path):
    with pytest.raises(JournalError, match="Dry run failed"):
        tool_edit_transaction(str(journal_path), "Esselunga", UNBALANCED_TXN, dry_run=True)
    assert "Esselunga" in journal_path.read_text(encoding="utf-8")


def test_edit_transaction_not_found(journal_path: Path):
    with pytest.raises(JournalError, match="not found"):
        tool_edit_transaction(str(journal_path), "no-such-payee-xyz", VALID_TXN)
    with pytest.raises(JournalError, match="not found"):
        tool_edit_transaction(str(journal_path), "no-such-payee-xyz", VALID_TXN, dry_run=True)


def test_edit_transaction_rejects_empty_inputs(journal_path: Path):
    with pytest.raises(JournalError, match="Search text cannot be empty"):
        tool_edit_transaction(str(journal_path), "  ", VALID_TXN)
    with pytest.raises(JournalError, match="New transaction text cannot be empty"):
        tool_edit_transaction(str(journal_path), "Esselunga", "  ")


def test_edit_transaction_ambiguous(journal_path: Path):
    journal_path.write_text(
        journal_path.read_text(encoding="utf-8")
        + "\n2026-03-01 Esselunga\n    expenses:groceries    9.00 EUR\n    assets:bank\n",
        encoding="utf-8",
    )
    with pytest.raises(JournalError, match="matches 2 transactions"):
        tool_edit_transaction(str(journal_path), "Esselunga", VALID_TXN)


def test_delete_transaction_dry_run_simulates_removal(journal_path: Path, tmp_path: Path):
    """dry_run must validate the journal as if the txn were removed."""
    before = journal_path.read_text(encoding="utf-8")
    result = tool_delete_transaction(str(journal_path), "Esselunga", dry_run=True)
    assert "successful" in result
    assert journal_path.read_text(encoding="utf-8") == before
    assert list(tmp_path.glob(".hledger_mcp_dry_run*")) == []


def test_delete_transaction_not_found(journal_path: Path):
    with pytest.raises(JournalError, match="not found"):
        tool_delete_transaction(str(journal_path), "no-such-payee-xyz")
    with pytest.raises(JournalError, match="Search text cannot be empty"):
        tool_delete_transaction(str(journal_path), "  ")


def test_add_price_and_account(journal_path: Path):
    assert (
        tool_add_price(str(journal_path), "2026-07-15", "EUR", "1.08 USD")
        == "Price directive added successfully."
    )
    assert "P 2026-07-15 EUR 1.08 USD" in journal_path.read_text(encoding="utf-8")
    assert (
        tool_add_account(str(journal_path), "assets:investments:gold")
        == "Account directive added successfully."
    )
    assert "account assets:investments:gold" in journal_path.read_text(encoding="utf-8")


def test_add_price_and_account_reject_empty(journal_path: Path):
    with pytest.raises(JournalError, match="Date cannot be empty"):
        tool_add_price(str(journal_path), " ", "EUR", "1.08 USD")
    with pytest.raises(JournalError, match="Commodity cannot be empty"):
        tool_add_price(str(journal_path), "2026-07-15", " ", "1.08 USD")
    with pytest.raises(JournalError, match="Price cannot be empty"):
        tool_add_price(str(journal_path), "2026-07-15", "EUR", " ")
    with pytest.raises(JournalError, match="Account name cannot be empty"):
        tool_add_account(str(journal_path), " ")


def test_check_reports_broken_journal(journal_path: Path):
    journal_path.write_text("this is not a valid journal txn\n", encoding="utf-8")
    result = tool_check(str(journal_path))
    assert "failed" in result.lower()
