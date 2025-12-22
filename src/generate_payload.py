# Created by AG on 22-12-2025

import random
from typing import Any, Dict, List
from copy import deepcopy
from src.utils import _drop_required_field
from src.payload_generation_utils import _generate_primitive_data_type
from src.schema_builders import AvroContract, _generate_union, _generate_dict_contract
from src.schema_builders import _generate_invalid_type, _generate_invalid_enum, _generate_invalid_required

def generate_valid_payload(
    contract: Any,
    rng: random.Random
) -> Any:
    if isinstance(contract, list):
        return _generate_union(contract, rng)

    if isinstance(contract, str):
        return _generate_primitive_data_type(contract, rng)

    if isinstance(contract, dict):
        return _generate_dict_contract(contract, rng)
    return None

def generate_invalid_payload(
    parsed_contract: AvroContract,
    rng: random.Random
) -> Dict[str, Any]:
    base_contract = generate_valid_payload(contract=parsed_contract, rng=rng)
    if not isinstance(base_contract, dict):
        return {
            "_is_invalid": True
        }

    if parsed_contract.get("type") != "record":
        return {
            "_is_invalid" : True
        }

    breaking_change: Dict[str, Any] = deepcopy(base_contract)
    breaking_changes: List = [
        _drop_required_field,
        _generate_invalid_type,
        _generate_invalid_enum,
        _generate_invalid_required
    ]
    select_breaking_changes = rng.choice(breaking_changes)
    return select_breaking_changes(breaking_change, parsed_contract, rng)
