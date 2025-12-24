# Created by AG on 23-12-2025

from __future__ import annotations

import time
import requests
from typing import Any, Dict
from dataclasses import dataclass


@dataclass
class Record:
    id: str
    is_valid: bool
    expected: str
    ok: bool
    status_code: int | None
    elapsed_time_ms: float
    error: str | None
    response: str | None

def runner(
    url: str,
    http_method: str,
    payload: Dict[str, Any],
    headers: Dict[str, str] | None = None,
    timeout: float = 10.0
) -> tuple[int | None, float, str | None, str | None]:
    header = {
        "Content-Type": "application/json"
    }
    if headers:
        header.update(headers)

    start_time = time.perf_counter()

    try:
        response = requests.request(
            method=http_method.upper(),
            url=url,
            headers=header,
            json=payload,
            timeout=timeout
        )

        elapsed_time = (time.perf_counter() - start_time) * 1000.0
        response_block = (response.text or "")[:500]
        return response.status_code, elapsed_time, None, response_block

    except Exception as err:
        elapsed_time = (time.perf_counter() - start_time) * 1000.0
        return None, elapsed_time, str(err), None


def parse_runner_response(
    is_valid: bool,
    status_code: int | None,
    *args,
    expect_2xx_for_valid: bool = True
) -> tuple[str, bool]:
    if status_code is None:
        expected = "pass" if is_valid else "fail"
        return expected, False

    if is_valid:
        expected = "pass" if is_valid else "fail"
        ok = (200 <= status_code < 300) if expect_2xx_for_valid else (status_code < 400)
        return expected, ok

    expected = "fail"
    ok = 400 <= status_code < 500
    return expected, ok
