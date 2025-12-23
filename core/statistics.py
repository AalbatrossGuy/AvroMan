# Created by AG on 23-12-2025

from __future__ import annotations

from typing import List
from runner import Record
from rich.table import Table
from rich.console import Console


def summary(
    records: List[Record]
) -> None:
    console = Console()
    good_count = sum(1 for record in records if record.ok)
    bad_count = len(records) - good_count

    table = Table(title="Contract Test Analysis")
    table.add_column("RecordID", no_wrap=True)
    table.add_column("is_valid", no_wrap=True)
    table.add_column("expected", no_wrap=True)
    table.add_column("status", no_wrap=True)
    table.add_column("ok", no_wrap=True)
    table.add_column("ms", justify="right", no_wrap=True)
    table.add_column("Response Snippet")

    for record in records:
        status_code = "-" if record.status_code is None else str(record.status_code)
        response_snippet = record.error if record.error else (record.response or "")
        table.add_row(
            record.id,
            str(record.is_valid),
            record.expected,
            status_code,
            str(record.ok),
            response_snippet[:200]
        )

    console.print(table)
    console.print(f"Total: {len(records)} GOOD: {good_count} BAD: {bad_count}")

