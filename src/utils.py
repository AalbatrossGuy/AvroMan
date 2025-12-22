# Created by AG on 20-12-2025

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List
from fastavro import parse_schema
from fastavro.types import Schema
from fastavro.validation import validate
from datetime import date, datetime, timezone
from schema_builders import AvroContract
from payload_generation_utils import _is_union_nullable

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


def _field_names(contract: AvroContract) -> List[str]:
    return [
        field["name"] for field in contract.get("fields", [])
    ]


def _field_names_required(contract: AvroContract) -> List[str]:
    required_field_names: List[str] = []
    for field in contract.get("fields", []):
        if not _is_union_nullable(field["type"]):
            required_field_names.append(field["name"])
    return required_field_names


def _fields_enum(contract: AvroContract) -> List[Dict[str, Any]]:
    return [
        field for field in contract.get("fields", []) 
        if isinstance(field.get("type"), dict) and field["type"].get("type") =="enum"
    ]

def _drop_required_field(
    inject_invalid: Dict[str, Any],
    contract: AvroContract,
    rng: random.Random
) -> Dict[str, Any]:
    required_field = _field_names_required(contract)
    if required_field:
        inject_invalid.pop(rng.choice(required_field), None)
        return inject_invalid

    field_names = _field_names(contract)
    if field_names:
        inject_invalid.pop(rng.choice(field_names), None)

    return inject_invalid


