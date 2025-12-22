# Created by AG on 22-12-2025

from __future__ import annotations
import random
from typing import Any, Dict
from generate_payload import generate_valid_payload
from payload_generation_utils import _generate_random_string
from utils import _probabilistic_choice, identify_logical_type
from payload_generation_utils import _union_contains_string, _rand_email_gen, _choose_union_branching
from payload_generation_utils import _is_email_field_valid, _is_string_valid_contract, _rand_fixed_bytes_to_b64

AvroContract = Dict[str, Any]

def _generate_record_field_value(
    field_name: str,
    field_contract: Any,
    field_default_value: Any | None,
    rng: random.Random
) -> Any:
    if field_default_value is not None and _probabilistic_choice(rng, 0.15):
        return field_default_value

    if _is_email_field_valid(field_name) and (_is_string_valid_contract(field_contract) or _union_contains_string(field_contract)):
        return _rand_email_gen(rng)

    return generate_valid_payload(field_contract, rng=rng)


def _generate_record(
    contract: AvroContract,
    rng: random.Random
) -> Dict[str, Any]:
    record: Dict[str, Any] = {}

    for field in contract.get("fields", []):
        name = field["name"]
        field_contract = field["type"]
        field_default = field.get("default", None) if "default" in field else None
        record[name] = _generate_record_field_value(name, field_contract, field_default, rng)

    return record


def _generate_array(
    contract: AvroContract,
    rng: random.Random
) -> list[Any]:
    items_contract = contract["items"]
    return [
        generate_valid_payload(items_contract, rng) for _ in range(rng.randint(0, 5))
    ]


def _generate_map(
    contract: AvroContract,
    rng: random.Random
) -> Dict[str, Any]:
    values_contract = contract["values"]
    return {
        _generate_random_string(rng, 3, 10): generate_valid_payload(values_contract, rng) for _ in range(rng.randint(0, 5))
    }


def _generate_enum(
    contract: AvroContract,
    rng:random.Random
) -> str:
    return rng.choice(contract["symbols"])


def _generate_union(
    contract: list[Any],
    rng: random.Random
) -> Any:
    selected_branch = _choose_union_branching(contract, rng=rng)
    return generate_valid_payload(selected_branch, rng)


def _generate_fixed(
    contract: AvroContract,
    rng: random.Random
) -> str:
    return _rand_fixed_bytes_to_b64(rng, int(contract["size"]))


def _generate_dict_contract(
    contract: AvroContract,
    rng: random.Random
) -> Any:
    logical_type = identify_logical_type(contract, rng)
    if logical_type is not None:
        return logical_type

    data_type = contract.get("type")

    if data_type == "record":
        return _generate_record(contract, rng)
    if data_type == "array":
        return _generate_array(contract, rng)
    if data_type == "map":
        return _generate_map(contract, rng)
    if data_type == "enum":
        return _generate_enum(contract, rng)
    if data_type == "fixed":
        return _generate_fixed(contract, rng)

