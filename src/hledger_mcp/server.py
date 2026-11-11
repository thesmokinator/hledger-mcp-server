from __future__ import annotations

import argparse

from mcp.server.fastmcp import FastMCP

from .journal import resolve_journal_path
from .tools.queries import (
    tool_accounts,
    tool_balance,
    tool_balancesheet,
    tool_cashflow,
    tool_commodities,
    tool_files,
    tool_incomestatement,
    tool_payees,
    tool_print,
    tool_register,
    tool_stats,
    tool_tags,
)
from .tools.mutations import (
    tool_add_account,
    tool_add_price,
    tool_add_transaction,
    tool_check,
    tool_delete_transaction,
    tool_edit_transaction,
)

mcp = FastMCP("hledger")

_journal_path_override: str | None = None


def _get_journal_path() -> str:
    """Resolve and return the journal path as a string."""
    return str(resolve_journal_path(_journal_path_override))


_REPORT_FORMATS = ("text", "csv", "json")


def _check_output_format(output_format: str, allowed: tuple[str, ...] = _REPORT_FORMATS) -> str:
    """Validate an output_format argument before touching the journal."""
    if output_format not in allowed:
        raise ValueError(f"Invalid output_format {output_format!r}: expected one of {', '.join(allowed)}")
    return output_format


# ── Read tools ──────────────────────────────────────────────────────


@mcp.tool(description="Show account balances with optional filters. Supports date ranges, depth limiting, tree/flat display, and period grouping (monthly/weekly/quarterly/yearly). Use output_format 'csv' or 'json' for machine-readable output.")
def hledger_balance(
    account: str | None = None,
    begin: str | None = None,
    end: str | None = None,
    period: str | None = None,
    depth: int | None = None,
    flat: bool = False,
    tree: bool = False,
    monthly: bool = False,
    weekly: bool = False,
    quarterly: bool = False,
    yearly: bool = False,
    invert: bool = False,
    commodity: str | None = None,
    output_format: str = "text",
) -> str:
    _check_output_format(output_format)
    return tool_balance(
        _get_journal_path(),
        account=account,
        begin=begin,
        end=end,
        period=period,
        depth=depth,
        flat=flat,
        tree=tree,
        monthly=monthly,
        weekly=weekly,
        quarterly=quarterly,
        yearly=yearly,
        invert=invert,
        commodity=commodity,
        output_format=output_format,
    )


@mcp.tool(description="Show transaction register with optional filters. Supports date ranges, depth limiting, and period grouping. Use output_format 'csv' or 'json' for machine-readable output.")
def hledger_register(
    account: str | None = None,
    begin: str | None = None,
    end: str | None = None,
    period: str | None = None,
    depth: int | None = None,
    monthly: bool = False,
    weekly: bool = False,
    quarterly: bool = False,
    yearly: bool = False,
    invert: bool = False,
    output_format: str = "text",
) -> str:
    _check_output_format(output_format)
    return tool_register(
        _get_journal_path(),
        account=account,
        begin=begin,
        end=end,
        period=period,
        depth=depth,
        monthly=monthly,
        weekly=weekly,
        quarterly=quarterly,
        yearly=yearly,
        invert=invert,
        output_format=output_format,
    )


@mcp.tool(description="Print transactions from the journal. Returns JSON by default for structured access to transaction data including amounts, dates, descriptions and source positions. Use output_format 'text' for plain journal syntax.")
def hledger_print(
    account: str | None = None,
    begin: str | None = None,
    end: str | None = None,
    output_format: str = "json",
) -> str:
    _check_output_format(output_format, ("json", "text"))
    return tool_print(
        _get_journal_path(),
        account=account,
        begin=begin,
        end=end,
        output_format=output_format,
    )


@mcp.tool(description="List all account names in the journal.")
def hledger_accounts() -> str:
    return tool_accounts(_get_journal_path())


@mcp.tool(description="List all payee/description strings found in transactions.")
def hledger_payees() -> str:
    return tool_payees(_get_journal_path())


@mcp.tool(description="List all commodities (currencies, stocks, etc.) used in the journal.")
def hledger_commodities() -> str:
    return tool_commodities(_get_journal_path())


@mcp.tool(description="List all tags used in transactions.")
def hledger_tags() -> str:
    return tool_tags(_get_journal_path())


@mcp.tool(description="List all files that compose the journal (resolves include directives).")
def hledger_files() -> str:
    return tool_files(_get_journal_path())


@mcp.tool(description="Show journal statistics: number of transactions, date range, commodities, etc.")
def hledger_stats() -> str:
    return tool_stats(_get_journal_path())


@mcp.tool(description="Generate an income statement (profit & loss). Supports date ranges and period grouping. Use output_format 'csv' or 'json' for machine-readable output.")
def hledger_incomestatement(
    begin: str | None = None,
    end: str | None = None,
    period: str | None = None,
    monthly: bool = False,
    quarterly: bool = False,
    yearly: bool = False,
    flat: bool = False,
    output_format: str = "text",
) -> str:
    _check_output_format(output_format)
    return tool_incomestatement(
        _get_journal_path(),
        begin=begin,
        end=end,
        period=period,
        monthly=monthly,
        quarterly=quarterly,
        yearly=yearly,
        flat=flat,
        output_format=output_format,
    )


@mcp.tool(description="Generate a balance sheet. Supports date ranges and period grouping. Use output_format 'csv' or 'json' for machine-readable output.")
def hledger_balancesheet(
    begin: str | None = None,
    end: str | None = None,
    period: str | None = None,
    monthly: bool = False,
    quarterly: bool = False,
    yearly: bool = False,
    flat: bool = False,
    output_format: str = "text",
) -> str:
    _check_output_format(output_format)
    return tool_balancesheet(
        _get_journal_path(),
        begin=begin,
        end=end,
        period=period,
        monthly=monthly,
        quarterly=quarterly,
        yearly=yearly,
        flat=flat,
        output_format=output_format,
    )


@mcp.tool(description="Generate a cash flow statement. Supports date ranges and period grouping. Use output_format 'csv' or 'json' for machine-readable output.")
def hledger_cashflow(
    begin: str | None = None,
    end: str | None = None,
    period: str | None = None,
    monthly: bool = False,
    quarterly: bool = False,
    yearly: bool = False,
    flat: bool = False,
    output_format: str = "text",
) -> str:
    _check_output_format(output_format)
    return tool_cashflow(
        _get_journal_path(),
        begin=begin,
        end=end,
        period=period,
        monthly=monthly,
        quarterly=quarterly,
        yearly=yearly,
        flat=flat,
        output_format=output_format,
    )


# ── Write tools ─────────────────────────────────────────────────────


@mcp.tool(description="Add a new transaction to the journal. The transaction must be valid hledger syntax. Use dry_run=True to validate without actually modifying the file.")
def hledger_add_transaction(
    transaction: str,
    dry_run: bool = False,
) -> str:
    return tool_add_transaction(_get_journal_path(), transaction, dry_run=dry_run)


@mcp.tool(description="Edit an existing transaction. Provide search_text to locate it (must match exactly one transaction) and new_transaction as the complete replacement. Use dry_run=True to validate first.")
def hledger_edit_transaction(
    search_text: str,
    new_transaction: str,
    dry_run: bool = False,
) -> str:
    return tool_edit_transaction(_get_journal_path(), search_text, new_transaction, dry_run=dry_run)


@mcp.tool(description="Delete a transaction from the journal. Provide search_text to identify it (date, description, or amount); it must match exactly one transaction. Use dry_run=True to preview first.")
def hledger_delete_transaction(
    search_text: str,
    dry_run: bool = False,
) -> str:
    return tool_delete_transaction(_get_journal_path(), search_text, dry_run=dry_run)


@mcp.tool(description="Add a P (price) directive to the journal. Example: date='2026-07-15', commodity='EUR', price='1.08 USD'.")
def hledger_add_price(
    date: str,
    commodity: str,
    price: str,
    dry_run: bool = False,
) -> str:
    return tool_add_price(_get_journal_path(), date, commodity, price, dry_run=dry_run)


@mcp.tool(description="Add an account directive to the journal. Example: account_name='assets:investments:gold'.")
def hledger_add_account(
    account_name: str,
    dry_run: bool = False,
) -> str:
    return tool_add_account(_get_journal_path(), account_name, dry_run=dry_run)


@mcp.tool(description="Validate the journal with hledger check. Returns whether the journal is valid or what errors were found.")
def hledger_check() -> str:
    return tool_check(_get_journal_path())


def run() -> None:
    """Entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="MCP server for hledger")
    parser.add_argument("--journal", "-f", help="Path to the main journal file (overrides LEDGER_FILE)")
    args = parser.parse_args()

    global _journal_path_override
    _journal_path_override = args.journal

    mcp.run()
