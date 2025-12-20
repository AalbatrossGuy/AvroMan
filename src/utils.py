# Created by AG on 20-12-2025

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from fastavro import parse_schema
from fastavro.types import Schema
from fastavro.validation import validate

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


