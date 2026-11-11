# hledger MCP

MCP server for [hledger](https://hledger.org) — plain-text accounting. It gives AI agents read/write access to your journals. Works with any MCP client (OpenCode, Claude Desktop, Cursor, …).

## Quick start

```bash
# Run directly (no install needed)
uvx hledger-mcp --journal /path/to/main.journal

# Or install globally
uv tool install hledger-mcp
hledger-mcp --journal /path/to/main.journal
```

The journal path can also come from the `LEDGER_FILE` environment variable.

## MCP client setup

OpenCode (`~/.config/opencode/opencode.json`):

```json
{
  "mcp": {
    "hledger": {
      "type": "local",
      "command": ["uvx", "hledger-mcp", "--journal", "/path/to/main.journal"],
      "enabled": true
    }
  }
}
```

Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "hledger": {
      "command": "uvx",
      "args": ["hledger-mcp", "--journal", "/path/to/main.journal"]
    }
  }
}
```

## Example

> _"How much did I spend on groceries last month?"_

The agent calls `hledger_balance(account="expenses:groceries", monthly=True)`.

> _"Record a 15 euro grocery purchase at Esselunga paid with my bank card."_

The agent calls `hledger_add_transaction()` with:

```
2026-07-28 Esselunga
    expenses:groceries    15.00 EUR
    assets:bank
```

Say _"check if it is valid first"_ and the agent will validate with `dry_run=True` before touching your journal.

## Tools

| Tool | Description |
|------|-------------|
| `hledger_balance` | Account balances, with filters and `output_format` (`text`/`csv`/`json`) |
| `hledger_register` | Transaction register, with filters and `output_format` (`text`/`csv`/`json`) |
| `hledger_print` | Transactions as JSON (default) or plain text |
| `hledger_accounts`, `hledger_payees`, `hledger_commodities`, `hledger_tags` | Names used in the journal |
| `hledger_stats`, `hledger_files` | Journal statistics; files behind `include` directives |
| `hledger_incomestatement`, `hledger_balancesheet`, `hledger_cashflow` | Financial reports, with `output_format` (`text`/`csv`/`json`) |
| `hledger_add_transaction`, `hledger_edit_transaction`, `hledger_delete_transaction` | Add, replace, or remove a transaction (edit/delete match exactly one) |
| `hledger_add_price`, `hledger_add_account` | Add a `P` price directive or an `account` directive |
| `hledger_check` | Validate the journal with `hledger check` |

## Safety

Every write is backed up, validated with `hledger check`, and rolled back on failure. `dry_run=True` validates against a temp file and never touches your journal.

## Requirements

- Python >= 3.12, [hledger](https://hledger.org/install.html) in `PATH`, [uv](https://docs.astral.sh/uv/getting-started/installation/) (or pip)
