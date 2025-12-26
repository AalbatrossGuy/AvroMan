# Created by AG on 22-12-2025

import re
import json
from pathlib import Path
from typing import Any, Tuple
from fastavro import parse_schema
from fastavro.validation import validate, ValidationError
from fastapi import FastAPI, HTTPException, Request

demo = FastAPI()

email_regex = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
AvroContract = parse_schema(json.loads(Path("contracts/sample.avsc").read_text(encoding="utf-8")))
valid_fields = {
    field["name"] for field in AvroContract["fields"]
}

def parse_error(message: str) -> Tuple[str, int]:
    message = message.lower()

    if "required" in message and "field" in message:
        return "missing fields", 422

    if "symbols" in message and ("not in" in message or "valid" in message):
        return "invalid enum", 422

    if "null" in message and ("expected" in message or "valid" in message or "allowed" in  message):
        return "value cannot be null", 422

    if "expected" in message or "is not a" in message or "not a valid" in message:
        return "data type mismatch", 422

    return "schema could not be validated", 422


def validate_request(
    payload: Any
) -> None:
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_request_body",
                "message": "Request must be JSON"
            },
        )

    invalid_fields = sorted(set(payload.keys()) - valid_fields)

    if invalid_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unknown_fields",
                "message": "Unknown fields in request body",
                "fields": invalid_fields
            },
        )

    if "email" in payload and payload["email"] is not None:
        if not isinstance(payload["email"], str) or not email_regex.match(payload["email"]):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "invalid_email",
                    "message": "Email is not valid",
                    "field": "email"
                },
            )

    try:
        validate(payload, AvroContract, raise_errors=True, strict=True)
    except ValidationError as err:
        error_message, status_code = parse_error(str(err))
        raise HTTPException(
            status_code=status_code,
            detail={
                "error": error_message,
                "message": "Schema validation failed",
                "details": str(err)
            },
        )

@demo.get("/status")
def status():
    return {
        "OK": True
    }

@demo.post("/events/usercreated")
async def usercreated(request: Request):
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_json_body",
                "message": "Request body is not valid JSON"
            }
        )

    validate_request(payload)

    return {
        "OK": True
    }
