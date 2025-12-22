# Created by AG on 22-12-2025

import random
from typing import Any
from payload_generation_utils import _generate_primitive_data_type
from schema_builders import _generate_union, _generate_dict_contract

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
