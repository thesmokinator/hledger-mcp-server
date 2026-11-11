"""Portable tests for journal safety helpers and path resolution.

Uses tmp_path journals from conftest.py — no dependency on any
personal journal file, so the suite runs identically locally and in CI.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from hledger_mcp.journal import (
    JournalError,
    append_transaction,
    delete_transaction,
    replace_transaction,
    resolve_journal_path,
)


def test_check_passes(journal_path: Path):
    from hledger_mcp.tools.mutations import tool_check

    result = tool_check(str(journal_path))
    assert "valid" in result.lower()


def test_append_then_delete_roundtrip(journal_path: Path):
    append_transaction(journal_path, "2026-03-10 Bookshop\n    expenses:books    25.00 EUR\n    assets:bank\n")
    assert "Bookshop" in journal_path.read_text(encoding="utf-8")
    assert delete_transaction(journal_path, "Bookshop") == 1
    assert "Bookshop" not in journal_path.read_text(encoding="utf-8")


def test_delete_no_match_returns_zero(journal_path: Path):
    before = journal_path.read_text(encoding="utf-8")
    assert delete_transaction(journal_path, "no-such-payee-xyz") == 0
    assert journal_path.read_text(encoding="utf-8") == before


def test_replace_no_match_returns_zero(journal_path: Path):
    before = journal_path.read_text(encoding="utf-8")
    assert replace_transaction(journal_path, "no-such-payee-xyz", "2026-01-01 X\n    a    1 EUR\n    b\n") == 0
    assert journal_path.read_text(encoding="utf-8") == before


def test_replace_roundtrip(journal_path: Path):
    assert (
        replace_transaction(
            journal_path,
            "Esselunga",
            "2026-01-15 Esselunga\n    expenses:groceries    20.00 EUR\n    assets:bank\n",
        )
        == 1
    )
    assert "20.00 EUR" in journal_path.read_text(encoding="utf-8")


def test_ambiguous_match_is_rejected(journal_path: Path):
    """A search text matching several transactions must not touch the first one."""
    journal_path.write_text(
        journal_path.read_text(encoding="utf-8")
        + "\n2026-03-01 Esselunga\n    expenses:groceries    9.00 EUR\n    assets:bank\n",
        encoding="utf-8",
    )
    before = journal_path.read_text(encoding="utf-8")
    with pytest.raises(JournalError, match="matches 2 transactions"):
        delete_transaction(journal_path, "Esselunga")
    with pytest.raises(JournalError, match="matches 2 transactions"):
        replace_transaction(journal_path, "Esselunga", "2026-01-01 X\n    a    1 EUR\n    b\n")
    assert journal_path.read_text(encoding="utf-8") == before


def test_delete_finds_transaction_in_included_file(journal_with_include: Path):
    """With include directives, the edit must land in the file holding the txn."""
    assert delete_transaction(journal_with_include, "Included shop") == 1
    main_content = journal_with_include.read_text(encoding="utf-8")
    assert "include extra.journal" in main_content  # main file structure untouched
    extra = (journal_with_include.parent / "extra.journal").read_text(encoding="utf-8")
    assert "Included shop" not in extra


def test_failed_validation_rolls_back(journal_path: Path):
    before = journal_path.read_text(encoding="utf-8")
    with pytest.raises(Exception):
        replace_transaction(
            journal_path,
            "Esselunga",
            "2026-01-15 Broken\n    expenses:groceries    25.00 EUR\n    assets:bank    10.00 EUR\n",
        )
    assert journal_path.read_text(encoding="utf-8") == before


def test_resolve_journal_path_env_override(journal_path: Path, monkeypatch):
    monkeypatch.setenv("LEDGER_FILE", str(journal_path))
    assert resolve_journal_path() == journal_path


def test_resolve_journal_path_missing_raises(tmp_path: Path):
    with pytest.raises(JournalError, match="not found"):
        resolve_journal_path(str(tmp_path / "missing.journal"))


def test_no_backup_files_left_behind(journal_path: Path, tmp_path: Path):
    from hledger_mcp.journal import safe_append

    delete_transaction(journal_path, "Esselunga")
    safe_append(journal_path, "2026-03-10 Bookshop\n    expenses:books    1.00 EUR\n    assets:bank\n", journal_path)
    assert list(tmp_path.glob("*.bak")) == []
