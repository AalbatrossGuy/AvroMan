# Created by AG on 21-12-2025
from __future__ import annotations

import base64
import random
import string
from typing import Any
from datetime import date, datetime, timezone

def _rand_bytes_to_b64(
    rng: random.Random,
    rand_min: int = 0,
    rand_max: int = 16
) -> str:
    raw_data = bytes(
        rng.getrandbits(8) for _ in range(rng.randint(rand_min, rand_max))
    )
    return base64.b64encode(raw_data).decode("ascii")

def _rand_fixed_bytes_to_b64(
    rng: random.Random,
    length: int
) -> str:
    raw_data = bytes(
        rng.getrandbits(8) for _ in range(length)
    )
    return base64.b64encode(raw_data).decode("ascii")

def _generate_random_string(
    rng: random.Random,
    minimum_length: int = 4,
    maximum_length: int = 20
) -> str:
    randnum = rng.randint(minimum_length, maximum_length)
    alphanum = string.ascii_letters + string.digits
    return "".join(rng.choice(alphanum) for _ in range(randnum))

def _rand_email_gen(
    rng: random.Random
) -> str:
    email_length = rng.randint(3, 12)
    email_characters = string.ascii_lowercase + string.digits
    email = "".join(rng.choice(email_characters) for _ in range(email_length))

    email_providers = [
        "gmail.com",
        "yahoo.com",
        "outlook.com",
        "icloud.com",
        "proton.me",
        "hotmail.com"
    ]

    return f"{email}@{rng.choice(email_providers)}"

def _is_branch_empty(branch: Any) -> bool:
    return branch == "null" or \
            (isinstance(branch, dict) and branch.get("type") == "null")


def _union_contains_string(contract: Any) -> bool:
    return isinstance(contract, list) and \
            any(
        branch == "string" or (isinstance(branch, dict) and branch.get("type") == "string") for branch in contract
        )


def _is_string_valid_contract(contract: Any) -> bool:
    return contract == "string" or \
            (isinstance(contract, dict) and contract.get("type") == "string")


def _is_email_field_valid(field_name: str) -> bool:
    field_name = field_name.lower()
    return field_name == "email" or field_name.endswith("_email") or field_name.endswith("email")


def _choose_union_branching(
    branches: list[Any],
    rng: random.Random
) -> Any:
    from src.utils import _probabilistic_choice
    empty_branches = [branch for branch in branches if _is_branch_empty(branch)]
    non_empty_branches = [branch for branch in branches if branch not in empty_branches]

    if empty_branches and _probabilistic_choice(rng, probability=0.25):
        return empty_branches[0]
    return rng.choice(non_empty_branches if non_empty_branches else branches)



def _is_union_nullable(field_contract: Any) -> bool:
    check: bool = isinstance(field_contract, list) and any(
        branch == "null" or (isinstance(branch, dict) and branch.get("type") == "null")
        for branch in field_contract
    )
    return check


def _generate_primitive_data_type(
    contract: str,
    rng: random.Random
) -> Any:
    if contract == "null":
        return None
    if contract == "boolean":
        return bool(rng.randint(0, 1))
    if contract == "int":
        return rng.randint(-1000, 5000)
    if contract == "long":
        return rng.randint(-10000, 200000)
    if contract in ["float", "double"]:
        return rng.uniform(-1000.0, 5000.0)
    if contract == "string":
        return _generate_random_string(rng=rng, minimum_length=5)
    if contract == "bytes":
        return _rand_bytes_to_b64(rng)

    return _generate_random_string(rng)

def _generate_wrong_data_type(
    contract: Any,
    rng: random.Random
) -> Any:
    if isinstance(contract, list):
        return {
            "invalid": "data_type"
        }

    if isinstance(contract, str):
        if contract in ("int", "long", "float", "double"):
            return "InvalidNumber"
        if contract == "boolean":
            return "InvalidBoolean"
        if contract == "string":
            return 1337
        return {
            "invalid": True
        }

    if isinstance(contract, dict):
        data_type = contract.get("type")
        if data_type == "array":
            return "InvalidArray"
        if data_type == "map":
            return ["Invalid", "Map"]
        if data_type == "record":
            return "InvalidRecord"
        if data_type == "enum":
            return "INVALID_SYMBOL"
        return {
            "invalid": "data_type"
        }

    return {
        "invalid": "dict"
    }
