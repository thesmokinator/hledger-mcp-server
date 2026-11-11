"""Shared pytest fixtures: self-contained hledger journals in tmp_path.

Every test builds its own journal file, so the suite runs anywhere
hledger is installed (including CI) with no personal data involved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

SAMPLE_JOURNAL = """\
2026-01-01 Opening balances
    assets:bank    1000.00 EUR
    equity:opening-balances

2026-01-15 Esselunga
    expenses:groceries    15.00 EUR
    assets:bank

2026-02-01 Employer
    assets:bank    2000.00 EUR
    income:salary
"""

VALID_TXN = """\
2026-03-10 Bookshop
    expenses:books    25.00 EUR
    assets:bank
"""

UNBALANCED_TXN = """\
2026-03-10 Bookshop
    expenses:books    25.00 EUR
    assets:bank    10.00 EUR
"""


@pytest.fixture
def journal_path(tmp_path: Path) -> Path:
    """A valid single-file journal."""
    journal = tmp_path / "main.journal"
    journal.write_text(SAMPLE_JOURNAL, encoding="utf-8")
    return journal


@pytest.fixture
def journal_with_include(tmp_path: Path) -> Path:
    """A main journal that includes a second file holding one transaction."""
    included = tmp_path / "extra.journal"
    included.write_text(
        "2026-02-10 Included shop\n"
        "    expenses:included    5.00 EUR\n"
        "    assets:bank\n",
        encoding="utf-8",
    )
    main = tmp_path / "main.journal"
    main.write_text("include extra.journal\n\n" + SAMPLE_JOURNAL, encoding="utf-8")
    return main
