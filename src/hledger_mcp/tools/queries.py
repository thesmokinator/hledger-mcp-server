from __future__ import annotations

from ..hledger import (
    run_hledger,
    load_accounts,
    load_commodities,
    load_journal_files,
    load_payees,
    load_tags,
)


def tool_balance(
    journal_path: str,
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
    """Generate a balance report."""
    args = ["balance"]

    if account:
        args.append(account)
    if begin:
        args.extend(["-b", begin])
    if end:
        args.extend(["-e", end])
    if period:
        args.extend(["-p", period])
    if depth:
        args.extend(["--depth", str(depth)])
    if flat:
        args.append("--flat")
    if tree:
        args.append("--tree")
    if monthly:
        args.append("-M")
    if weekly:
        args.append("-W")
    if quarterly:
        args.append("-Q")
    if yearly:
        args.append("-Y")
    if invert:
        args.append("--invert")
    if commodity:
        args.extend(["-X", commodity])

    if output_format == "csv":
        args.extend(["-O", "csv"])
    elif output_format == "json":
        args.extend(["-O", "json"])

    return run_hledger(*args, file=journal_path)


def tool_register(
    journal_path: str,
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
    """Generate a transaction register report."""
    args = ["register"]

    if account:
        args.append(account)
    if begin:
        args.extend(["-b", begin])
    if end:
        args.extend(["-e", end])
    if period:
        args.extend(["-p", period])
    if depth:
        args.extend(["--depth", str(depth)])
    if monthly:
        args.append("-M")
    if weekly:
        args.append("-W")
    if quarterly:
        args.append("-Q")
    if yearly:
        args.append("-Y")
    if invert:
        args.append("--invert")

    if output_format == "csv":
        args.extend(["-O", "csv"])
    elif output_format == "json":
        args.extend(["-O", "json"])

    return run_hledger(*args, file=journal_path)


def tool_print(
    journal_path: str,
    account: str | None = None,
    begin: str | None = None,
    end: str | None = None,
    output_format: str = "json",
) -> str:
    """Print transactions in journal or JSON format."""
    args = ["print"]
    if account:
        args.append(account)
    if begin:
        args.extend(["-b", begin])
    if end:
        args.extend(["-e", end])
    if output_format == "json":
        args.extend(["-O", "json"])
    return run_hledger(*args, file=journal_path)


def tool_accounts(journal_path: str) -> str:
    """List all account names."""
    return "\n".join(load_accounts(journal_path))


def tool_payees(journal_path: str) -> str:
    """List all payee/description strings."""
    return "\n".join(load_payees(journal_path))


def tool_commodities(journal_path: str) -> str:
    """List all commodities in the journal."""
    return "\n".join(load_commodities(journal_path))


def tool_tags(journal_path: str) -> str:
    """List all tags in the journal."""
    return "\n".join(load_tags(journal_path))


def tool_files(journal_path: str) -> str:
    """List all files composing the journal (resolves include directives)."""
    return "\n".join(load_journal_files(journal_path))


def tool_stats(journal_path: str) -> str:
    """Show journal statistics."""
    return run_hledger("stats", file=journal_path)


def tool_incomestatement(
    journal_path: str,
    begin: str | None = None,
    end: str | None = None,
    period: str | None = None,
    monthly: bool = False,
    quarterly: bool = False,
    yearly: bool = False,
    flat: bool = False,
    output_format: str = "text",
) -> str:
    """Generate an income statement (profit & loss)."""
    args = ["is"]
    if begin:
        args.extend(["-b", begin])
    if end:
        args.extend(["-e", end])
    if period:
        args.extend(["-p", period])
    if monthly:
        args.append("-M")
    if quarterly:
        args.append("-Q")
    if yearly:
        args.append("-Y")
    if flat:
        args.append("--flat")
    if output_format == "csv":
        args.extend(["-O", "csv"])
    elif output_format == "json":
        args.extend(["-O", "json"])
    return run_hledger(*args, file=journal_path)


def tool_balancesheet(
    journal_path: str,
    begin: str | None = None,
    end: str | None = None,
    period: str | None = None,
    monthly: bool = False,
    quarterly: bool = False,
    yearly: bool = False,
    flat: bool = False,
    output_format: str = "text",
) -> str:
    """Generate a balance sheet."""
    args = ["bs"]
    if begin:
        args.extend(["-b", begin])
    if end:
        args.extend(["-e", end])
    if period:
        args.extend(["-p", period])
    if monthly:
        args.append("-M")
    if quarterly:
        args.append("-Q")
    if yearly:
        args.append("-Y")
    if flat:
        args.append("--flat")
    if output_format == "csv":
        args.extend(["-O", "csv"])
    elif output_format == "json":
        args.extend(["-O", "json"])
    return run_hledger(*args, file=journal_path)


def tool_cashflow(
    journal_path: str,
    begin: str | None = None,
    end: str | None = None,
    period: str | None = None,
    monthly: bool = False,
    quarterly: bool = False,
    yearly: bool = False,
    flat: bool = False,
    output_format: str = "text",
) -> str:
    """Generate a cash flow statement."""
    args = ["cf"]
    if begin:
        args.extend(["-b", begin])
    if end:
        args.extend(["-e", end])
    if period:
        args.extend(["-p", period])
    if monthly:
        args.append("-M")
    if quarterly:
        args.append("-Q")
    if yearly:
        args.append("-Y")
    if flat:
        args.append("--flat")
    if output_format == "csv":
        args.extend(["-O", "csv"])
    elif output_format == "json":
        args.extend(["-O", "json"])
    return run_hledger(*args, file=journal_path)
