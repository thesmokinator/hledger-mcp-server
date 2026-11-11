from __future__ import annotations

import shutil
from pathlib import Path

from .hledger import HledgerError, check_journal, load_journal_files


class JournalError(Exception):
    """Raised when a journal modification fails validation."""


def _backup(file_path: Path) -> Path:
    """Create a timestamped backup of the given file."""
    import time

    backup = file_path.with_suffix(file_path.suffix + f".{int(time.time())}.bak")
    if file_path.exists():
        shutil.copy2(file_path, backup)
    return backup


def _restore(file_path: Path, backup: Path) -> None:
    """Restore file from backup."""
    if backup.exists():
        shutil.copy2(backup, file_path)
    if file_path.exists():
        shutil.copystat(backup, file_path)


def _cleanup_backup(backup: Path) -> None:
    """Remove a backup file."""
    backup.unlink(missing_ok=True)


def _validate_and_finalize(main_journal: Path, source_file: Path, backup: Path) -> None:
    """Validate the journal after a modification; roll back on failure."""
    try:
        check_journal(main_journal)
    except HledgerError as exc:
        _restore(source_file, backup)
        _cleanup_backup(backup)
        raise JournalError(f"Journal validation failed: {exc}") from exc
    _cleanup_backup(backup)


def safe_write(
    file_path: Path,
    content: str,
    main_journal: Path,
    validate: bool = True,
) -> None:
    """Safely overwrite a journal file with backup/restore/validate.

    Args:
        file_path: The file to write to.
        content: The full new content of the file.
        main_journal: The main journal for validation (may equal file_path).
        validate: Whether to run hledger check after writing.
    """
    backup = _backup(file_path)
    try:
        file_path.write_text(content, encoding="utf-8")
        if validate:
            _validate_and_finalize(main_journal, file_path, backup)
        else:
            _cleanup_backup(backup)
    except Exception:
        _restore(file_path, backup)
        _cleanup_backup(backup)
        raise


def safe_append(
    file_path: Path,
    lines: str | list[str],
    main_journal: Path,
    validate: bool = True,
) -> None:
    """Safely append lines to a journal file with backup/restore/validate."""
    if isinstance(lines, list):
        text = "\n".join(lines) + "\n"
    else:
        text = lines if lines.endswith("\n") else lines + "\n"

    backup = _backup(file_path)
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(text)
        if validate:
            _validate_and_finalize(main_journal, file_path, backup)
        else:
            _cleanup_backup(backup)
    except Exception:
        _restore(file_path, backup)
        _cleanup_backup(backup)
        raise


def append_transaction(
    journal_path: Path,
    transaction_text: str,
) -> None:
    """Append a new transaction to the journal and validate."""
    safe_append(journal_path, transaction_text.strip() + "\n\n", journal_path)


def _block_bounds(lines: list[str], idx: int) -> tuple[int, int]:
    """Return the (start, end) line bounds of the blank-line-delimited block holding idx."""
    start = idx
    while start > 0 and lines[start - 1].strip():
        start -= 1
    end = idx
    while end < len(lines) - 1 and lines[end].strip():
        end += 1
    return start, end


def _locate_blocks(content: str, search_text: str) -> list[tuple[int, int]]:
    """Return the deduped (start, end) blocks whose lines contain search_text."""
    lines = content.split("\n")
    blocks: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        if search_text in line:
            block = _block_bounds(lines, i)
            if block not in blocks:
                blocks.append(block)
    return blocks


def _remove_block(content: str, search_text: str) -> str | None:
    """Remove the unique block containing search_text.

    Returns the new content, None if search_text is absent.
    Raises JournalError if search_text matches more than one block.
    """
    blocks = _locate_blocks(content, search_text)
    if not blocks:
        return None
    if len(blocks) > 1:
        raise JournalError(
            f"Search text matches {len(blocks)} transactions, refusing to guess: {search_text}. "
            "Provide more specific text."
        )
    start, end = blocks[0]
    lines = content.split("\n")
    del lines[start : end + 1]
    while start > 0 and not lines[start - 1].strip():
        del lines[start - 1]
        start -= 1
    return "\n".join(lines) + "\n"


def _replace_block(content: str, search_text: str, replacement: str) -> str | None:
    """Replace the unique block containing search_text with replacement.

    Returns the new content, None if search_text is absent.
    Raises JournalError if search_text matches more than one block.
    """
    blocks = _locate_blocks(content, search_text)
    if not blocks:
        return None
    if len(blocks) > 1:
        raise JournalError(
            f"Search text matches {len(blocks)} transactions, refusing to guess: {search_text}. "
            "Provide more specific text."
        )
    start, end = blocks[0]
    lines = content.split("\n")
    lines[start : end + 1] = replacement.strip().split("\n")
    return "\n".join(lines) + "\n"


def _journal_files(main_journal: Path) -> list[Path]:
    """All files composing the journal (resolves include directives).

    Falls back to the main file alone when hledger cannot list them
    (e.g. the journal is currently invalid).
    """
    try:
        files = [Path(f) for f in load_journal_files(main_journal) if f.strip()]
        if files:
            return files
    except Exception:
        pass
    return [main_journal]


def _apply_to_unique_file(
    journal_path: Path,
    search_text: str,
    transform: str,
    replacement: str = "",
) -> tuple[Path, str] | None:
    """Apply a block transform in the single file holding search_text.

    Returns (owning_file, new_content), or None when nothing matches.
    Raises JournalError when several transactions match.
    """
    matches: list[tuple[Path, str, str]] = []
    for candidate in _journal_files(journal_path):
        try:
            content = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        if search_text not in content:
            continue
        if transform == "delete":
            new_content = _remove_block(content, search_text)
        else:
            new_content = _replace_block(content, search_text, replacement)
        if new_content is not None and new_content != content:
            matches.append((candidate, content, new_content))
    if not matches:
        return None
    if len(matches) > 1:
        files = sorted({str(path) for path, _, _ in matches})
        raise JournalError(
            f"Search text matches {len(matches)} transactions, refusing to guess: {search_text} "
            f"(files: {', '.join(files)}). Provide more specific text."
        )
    found_file, _, found_new_content = matches[0]
    return found_file, found_new_content


def preview_delete(journal_path: Path, search_text: str) -> tuple[Path, str] | None:
    """Compute the deletion without writing; see _apply_to_unique_file."""
    return _apply_to_unique_file(journal_path, search_text, "delete")


def preview_replace(journal_path: Path, search_text: str, replacement: str) -> tuple[Path, str] | None:
    """Compute the replacement without writing; see _apply_to_unique_file."""
    return _apply_to_unique_file(journal_path, search_text, "replace", replacement)


def delete_transaction(
    journal_path: Path,
    search_text: str,
) -> int:
    """Delete the transaction uniquely matching the given text.

    The match is searched across all files composing the journal (include
    directives resolved). Returns 1 if a transaction was removed, 0 if none
    matched. Raises JournalError if several transactions match.
    """
    found = _apply_to_unique_file(journal_path, search_text, "delete")
    if found is None:
        return 0
    found_file, new_content = found
    safe_write(found_file, new_content, journal_path)
    return 1


def replace_transaction(
    journal_path: Path,
    search_text: str,
    replacement: str,
) -> int:
    """Replace the transaction uniquely matching search_text with replacement.

    The match is searched across all files composing the journal (include
    directives resolved). Returns 1 if replaced, 0 if no match.
    Raises JournalError if several transactions match.
    """
    found = _apply_to_unique_file(journal_path, search_text, "replace", replacement)
    if found is None:
        return 0
    found_file, new_content = found
    safe_write(found_file, new_content, journal_path)
    return 1


def append_price(
    journal_path: Path,
    date: str,
    commodity: str,
    price: str,
) -> None:
    """Append a P (price) directive to the journal.

    Example: P 2026-07-15 EUR 1.08 USD
    """
    price_line = f"P {date} {commodity} {price}"
    safe_append(journal_path, price_line + "\n", journal_path)


def resolve_journal_path(custom_path: str | None = None) -> Path:
    """Resolve the journal file path.

    Priority:
    1. custom_path argument
    2. LEDGER_FILE environment variable
    3. ~/.hledger.journal (default)
    """
    import os

    path = custom_path or os.environ.get("LEDGER_FILE") or os.path.expanduser("~/.hledger.journal")
    resolved = Path(path)
    if not resolved.exists():
        raise JournalError(f"Journal file not found: {resolved}")
    return resolved
