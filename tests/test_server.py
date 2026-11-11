"""Tests for the MCP layer: every query/report tool exposes output_format."""

from __future__ import annotations

import inspect

import pytest

from hledger_mcp import server


@pytest.mark.parametrize(
    "tool_name",
    [
        "hledger_balance",
        "hledger_register",
        "hledger_incomestatement",
        "hledger_balancesheet",
        "hledger_cashflow",
    ],
)
def test_output_format_exposed_with_text_default(tool_name: str):
    params = inspect.signature(getattr(server, tool_name)).parameters
    assert "output_format" in params, f"{tool_name} should expose output_format"
    assert params["output_format"].default == "text"


def test_print_defaults_to_json():
    params = inspect.signature(server.hledger_print).parameters
    assert "output_format" in params
    assert params["output_format"].default == "json"


@pytest.mark.parametrize(
    "tool_name",
    [
        "hledger_balance",
        "hledger_register",
        "hledger_incomestatement",
        "hledger_balancesheet",
        "hledger_cashflow",
        "hledger_print",
    ],
)
def test_invalid_output_format_rejected_without_touching_journal(tool_name: str):
    with pytest.raises(ValueError, match="output_format"):
        getattr(server, tool_name)(output_format="xml")
