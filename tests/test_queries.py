"""Tests for the read/report tools in hledger_mcp.tools.queries."""

from __future__ import annotations

from pathlib import Path

from hledger_mcp.tools import queries


def test_balance_contains_expected_accounts(journal_path: Path):
    out = queries.tool_balance(str(journal_path))
    assert "assets:bank" in out
    assert "expenses:groceries" in out


def test_balance_json_and_csv_formats(journal_path: Path):
    import json

    as_json = queries.tool_balance(str(journal_path), output_format="json")
    parsed = json.loads(as_json)
    assert isinstance(parsed, list) and parsed, "balance JSON should be a non-empty list"
    as_csv = queries.tool_balance(str(journal_path), output_format="csv")
    assert "account" in as_csv.lower()


def test_register_and_print(journal_path: Path):
    import json

    register = queries.tool_register(str(journal_path))
    assert "Esselunga" in register
    printed = queries.tool_print(str(journal_path))
    txns = json.loads(printed)
    assert len(txns) == 3
    assert any(t["tdescription"] == "Esselunga" for t in txns)


def test_print_text_format(journal_path: Path):
    out = queries.tool_print(str(journal_path), output_format="text")
    assert "Esselunga" in out
    assert not out.lstrip().startswith("[")


def test_listings(journal_path: Path):
    assert "assets:bank" in queries.tool_accounts(str(journal_path)).splitlines()
    assert "Esselunga" in queries.tool_payees(str(journal_path)).splitlines()
    assert "EUR" in queries.tool_commodities(str(journal_path)).splitlines()
    assert "journal" in queries.tool_files(str(journal_path)).lower()


def test_stats_and_reports(journal_path: Path):
    assert "3" in queries.tool_stats(str(journal_path))  # three transactions
    assert "groceries" in queries.tool_incomestatement(str(journal_path)).lower()
    assert "assets" in queries.tool_balancesheet(str(journal_path)).lower()
    assert "bank" in queries.tool_cashflow(str(journal_path)).lower()


def test_balance_filters(journal_path: Path):
    out = queries.tool_balance(
        str(journal_path), account="expenses:groceries", begin="2026-01-01", end="2026-01-31"
    )
    assert "groceries" in out
    assert "salary" not in out.lower()
