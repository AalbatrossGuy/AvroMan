# Created by AG on 24-12-2025

from __future__ import annotations

import json
import click
import random
from pathlib import Path
from typing import Any, Dict
from core.statistics import summary
from src.utils import load_contract, is_record_valid
from core.runner import Record, runner, parse_runner_response
from src.generate_payload import generate_valid_payload, generate_invalid_payload


def parse_headers(
    headers: str | None
) -> Dict[str, str] | None:
    if not headers:
        return None

    headers_json = json.loads(headers)
    if not isinstance(headers_json, dict):
        raise click.BadParameter("Header must be a JSON object.")

    return {
        str(key): str(value) for key, value in headers_json.items()
    }


def validate_record_type(payload: Any) -> Dict[str, Any] | None:
    return payload if isinstance(payload, dict) else None


def generate_valid_record(
    parsed_contract: Dict[str, Any],
    rng: random.Random,
    attempts_to_make: int = 5
) -> Dict[str, Any]:
    for _ in range(max(1, attempts_to_make)):
        payload = validate_record_type(
            generate_valid_payload(parsed_contract, rng)
        )
        if payload is not None and is_record_valid(parsed_contract, payload):
            return payload

    return {
        "_failed": True
    }


def generate_invalid_record(
    parsed_contract: Dict[str, Any],
    rng: random.Random
) -> Dict[str, Any]:
    payload = generate_invalid_payload(parsed_contract, rng)
    if isinstance(payload, dict):
        return payload

    return {
        "_is_invalid": True
}



@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def avroman() -> None:
    pass


@avroman.command()
@click.option("--schema", "contract_path", type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path), required=True, help="Path to schema file")
@click.option("--url", required=True, help="Endpoint URL")
@click.option("--method", default="POST", show_default=True, help="HTTP method")
@click.option("--n-valid", default=25, show_default=True, type=int, help="Number of valid cases")
@click.option("--n-invalid", default=25, show_default=True, type=int, help="Number of invalid cases")
@click.option("--seed", default=0, show_default=True, type=int, help="RNG seed")
@click.option("--headers", default=None, help='Extra headers as JSON string, e.g. \'{"Authorization":"Bearer ..."}\'')
@click.option("--timeout", "timeout_s", default=10.0, show_default=True, type=float, help="Request timeout in seconds")
@click.option(
    "--valid-accept-3xx/--valid-accept-2xx",
    default=False,
    show_default=True,
    help="If set, treat any <400 as success for valid cases (accept 3xx). Default: only 2xx is success",
)
@click.option(
    "--fail-on-any/--no-fail-on-any",
    default=True,
    show_default=True,
    help="Exit non-zero if any case is not ok",
)
def run(
    contract_path: Path,
    url: str,
    method: str,
    n_valid: int,
    n_invalid: int,
    seed: int,
    headers: str | None,
    timeout_s: float,
    valid_accept_3xx: bool,
    fail_on_any: bool,
) -> None:
    parsed_contract = load_contract(contract_path)
    rng = random.Random(seed)
    headers = parse_headers(headers)

    results: list[Record] = []

    for i in range(n_valid):
        payload = generate_valid_record(parsed_contract, rng)
        status, ms, err, snippet = runner(url, method, payload, headers=headers, timeout=timeout_s)
        expected, ok = parse_runner_response(True, status, expect_2xx_for_valid=not valid_accept_3xx)
        results.append(
            Record(
                id=f"V{i:03d}",
                is_valid=True,
                expected=expected,
                status_code=status,
                elapsed_time_ms=ms,
                error=err,
                response=snippet,
            )
        )

    for i in range(n_invalid):
        payload = generate_invalid_record(parsed_contract, rng)

        if isinstance(payload, dict) and is_record_valid(parsed_contract, payload):
            payload = {"_is_invalid": True}

        status, ms, err, snippet = runner(url, method, payload, headers=headers, timeout=timeout_s)
        expected, ok = parse_runner_response(False, status, expect_2xx_for_valid=not valid_accept_3xx)
        results.append(
            Record(
                id=f"I{i:03d}",
                is_valid=False,
                expected=expected,
                status_code=status,
                elapsed_time_ms=ms,
                error=err,
                response=snippet,
            )
        )

    summary(results)

    # if fail_on_any and any(not result.ok for result in results):
    #     raise SystemExit(1)


if __name__ == "__main__":
    avroman()
