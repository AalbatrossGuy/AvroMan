# Created by AG on 22-12-2025

import json
from pathlib import Path
from fastavro import parse_schema
from fastavro.validation import validate, ValidationError
from fastapi import FastAPI, HTTPException, Request

demo = FastAPI()

AvroContract = parse_schema(json.loads(Path("contracts/sample.avsc").read_text(encoding="utf-8")))
valid_fields = {
    field["name"] for field in AvroContract["fields"]
}

@demo.get("/status")
def status():
    return {
        "OK": True
    }

@demo.post("/events/usercreated")
async def usercreated(request: Request):
    payload = await request.json()
    invalid_fields = set(payload.keys()) - valid_fields

    if invalid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid fields: {sorted(invalid_fields)}")

    try:
        valid_payload_data = validate(payload, AvroContract)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if not valid_payload_data:
        raise HTTPException(status_code=422, detail="Schema validation failed")

    return {
        "OK": True
    }
