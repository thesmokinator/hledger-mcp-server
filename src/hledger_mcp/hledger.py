from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


class HledgerError(Exception):
    """Raised when an hledger CLI command fails."""


def run_hledger(*args: str, file: str | Path | None = None, timeout: int = 30) -> str:
    """Execute an hledger command and return stdout.

    Args:
        *args: Arguments passed to the hledger binary.
        file: Optional journal file path (uses LEDGER_FILE env var if omitted).
        timeout: Maximum seconds to wait for the command.

    Returns:
        The command's stdout as a string.

    Raises:
        HledgerError: If hledger is not found or exits with a non-zero status.
    """
    cmd = ["hledger", *args]
    if file:
        cmd.extend(["-f", str(file)])

    env = {**os.environ}
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            env=env,
        )
    except FileNotFoundError:
        raise HledgerError("hledger executable not found. Is hledger installed?") from None
    except subprocess.TimeoutExpired:
        raise HledgerError(f"hledger command timed out after {timeout}s: {' '.join(cmd)}") from None

    if result.returncode != 0:
        raise HledgerError(result.stderr.strip() or f"hledger exited with code {result.returncode}")

    return result.stdout


def check_journal(file: str | Path) -> None:
    """Validate a journal file via hledger check.

    Raises HledgerError if the journal is invalid.
    """
    run_hledger("check", "-f", str(file))


def load_transactions(file: str | Path) -> list[dict]:
    """Load all transactions from a journal in JSON format."""
    output = run_hledger("print", "-O", "json", file=file)
    if not output.strip():
        return []
    return json.loads(output)


def load_accounts(file: str | Path) -> list[str]:
    """Load all account names from a journal."""
    output = run_hledger("accounts", file=file)
    return [line.strip() for line in output.splitlines() if line.strip()]


def load_payees(file: str | Path) -> list[str]:
    """Load all payee/description strings from a journal."""
    output = run_hledger("descriptions", file=file)
    return [line.strip() for line in output.splitlines() if line.strip()]


def load_commodities(file: str | Path) -> list[str]:
    """Load all commodities from a journal."""
    output = run_hledger("commodities", file=file)
    return [line.strip() for line in output.splitlines() if line.strip()]


def load_tags(file: str | Path) -> list[str]:
    """Load all tags from a journal."""
    output = run_hledger("tags", file=file)
    return [line.strip() for line in output.splitlines() if line.strip()]


def load_journal_files(file: str | Path) -> list[str]:
    """Discover all files composing the journal (resolves include directives)."""
    output = run_hledger("files", file=file)
    return [line.strip() for line in output.splitlines() if line.strip()]
