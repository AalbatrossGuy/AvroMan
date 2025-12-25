# Created by AG on 23-12-2025

from __future__ import annotations

from typing import List, Any
from core.runner import Record
from rich.table import Table
from rich.console import Console


def _as_bool(string: Any) -> bool:
    if isinstance(string, bool):
        return string
    if isinstance(string, str):
        return string.strip().lower() in {"true", "1", "yes", "y"}
    if isinstance(string, int):
        return string != 0
    return False


def summary(records: List[Record]) -> None:
    console = Console(width=140)
    # console.print(type(records[0].ok), records[0].ok)

    # good_count = sum(1 for record in records if _as_bool(record.ok))
    # bad_count = len(records) - good_count

    good_count = sum(1 for record in records if (record.expected or "").strip().lower() == "pass")
    bad_count = sum(1 for record in records if (record.expected or "").strip().lower() == "fail")


    table = Table(title="Contract test analysis", expand=True)
    table.add_column("record", width=6, no_wrap=True)
    table.add_column("is_valid", width=8, no_wrap=True)
    table.add_column("expected", width=8, no_wrap=True)
    table.add_column("status", width=6, no_wrap=True)
    table.add_column("ms", justify="right", width=8, no_wrap=True)
    table.add_column("response", overflow="fold")

    for record in records:
        status = "-" if record.status_code is None else str(record.status_code)
        response_snippet = (record.error or record.response or "")[:300]

        table.add_row(
            record.id,
            "yes" if _as_bool(record.is_valid) else "no",
            record.expected,
            status,
            f"{record.elapsed_time_ms:.1f}",
            response_snippet,
        )

    console.print(table)
    console.print(f"Total: {len(records)}  Good: {good_count}  Bad: {bad_count}")

