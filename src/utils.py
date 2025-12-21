# Created by AG on 20-12-2025

from __future__ import annotations

import json
import random
import string
from pathlib import Path
from typing import Any, Dict
from fastavro import parse_schema
from fastavro.types import Schema
from fastavro.validation import validate
from datetime import date, datetime, timezone

Contract = Dict[str, Any]

def load_contract(
        contract_path: str | Path
) -> Schema:
    contract_path = Path(contract_path)
    contract_data = json.loads(contract_path.read_text(encoding="utf-8"))
    return parse_schema(contract_data)

def is_record_valid(
    parsed_contract: Dict[str, Any],
    record: Dict[str, Any]
) -> bool:
    try:
        return bool(validate(record, parsed_contract))
    except Exception:
        return False


def _probabilistic_choice(
    rng: random.Random,
    probability: float = 0.3
) -> bool:
    return rng.random() < probability

def identify_logical_type(
    contract: Contract,
    rng: random.Random
) -> Any:
    logical_type = contract.get("logicalType")
    if logical_type == "date":
        set_date = date(
            2000 + rng.randint(0, 30), rng.randint(1, 12), rng.randint(1, 28)
        ) 
        epoch = date(1970, 1, 1)
        return (set_date - epoch).days

    if logical_type in ("timestamp-millis", "timestamp-micros"):
        now = datetime.now(tz=timezone.utc)
        millisecond = int(now.timestamp() * 1000)

        if logical_type == "timestamp-micros":
            return millisecond * 1000
        return millisecond

    return None
