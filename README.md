# AvroMan

## What is Apache Avro?
Apache Avro is a **data serialization system**. It provides **rich** data structures, a **compact** **fast** binary data format, a **container** file to store persistent data, **remote procedure call** (RPC), **simple** integration with dynamic languages.
Code generation is not required to read or write data files nor to use or implement RPC protocols. Code generation as an optional optimization, only worth implementing for statically typed languages.

## What is Avro Schemas/Contracts?
Avro relies on **schemas**. When Avro data is read, the schema used when writing it is always present. This permits each datum to be written with **no per-value overheads**, making serialization both **fast** and **small**. This also facilitates use with dynamic, scripting languages, since data, together with its schema, is fully **self-describing**. When Avro data is stored in a file, its schema is stored with it, so that files may be processed later by any program. If the program reading the data expects a different schema this can be easily resolved, since both schemas are present. When Avro is used in RPC, the client and server exchange schemas in the **connection handshake**. (This can be optimized so that, for most calls, no schemas are actually transmitted.) Since both client and server both have the other’s full schema, **correspondence** between same named fields, missing fields, extra fields, etc. can all be easily resolved.

Avro schemas are defined with JSON . This facilitates implementation in languages that already have JSON libraries.

## What is AvroMan?

AvroMan is a tool that uses an Avro schema (`.avsc`) as the contract for an HTTP endpoint. It automatically generates valid and invalid JSON payloads from the schema, sends them to your API, and prints a report showing whether the service accepted valid input and rejected invalid input. It shows valuable details like how long the api took to respond, what was the exact error message and what status code it returned for valid/invalid payloads.

It is designed for testing how your API responds to a wide range of Avro schemas, essentially, [Postman](https://github.com/postmanlabs) but for Avro.

## What it does

- Generate **valid** payloads that conform to [avro schema](https://avro.apache.org/docs/1.11.1/specification/) standards.
- Generate **invalid** payloads by changing valid payloads deviating from the standards.
- Send requests to your **custom** endpoint.
- Show a proper analysis stating status codes, time, API response block, etc. in a tabular form.
- Display summary of total number of payloads formed with deeper statistics of the number of valid/invalid payloads.


## Project Structure

```text
.
├─ contracts/
│  └─ sample.avsc
├─ api_demos/
│  └─ demo_fastapi.py
├─ src/
│  ├─ __init__.py
│  ├─ avroman.py
│  ├─ utils.py
│  ├─ generate_payload.py
│  ├─ payload_generation_utils.py
│  └─ schema_builders.py
├─ core/
│  ├─ statistics.py
│  └─ runner.py
│
├─ LICENSE
└─ README.md
```

## Requirements
- `fastavro`
- `requests`
- `click`
- `rich`
- `fastapi`

## Installation
Install dependencies
```
pip3 install -r requirements.txt
```
FastAPI:
```
python3 -m uvicorn api_demos.demo_fastapi:demo --host 127.0.0.1 --port 8080
```
Run AvroMan
```
python -m src.avroman run \
  --schema contracts/sample.avsc \
  --url http://127.0.0.1:8080/events/usercreated \
  --method POST \
  --headers "{\"Authorization\":\"Bearer TOKEN\"}" \
  --n-valid 30 \
  --n-invalid 30 \
--seed 19
```
## CLI Arguments
- `--schema`: path to schema file.

- `--url`: custom endpoint to test.

- `--method`: HTTP method [default: `POST`].

- `--n-valid`: number of valid payloads to generate.

- `--n-invalid`: number of invalid payloads to generate.

- `--seed`: RNG seed for reproducible test data.

- `--headers`: JSON string for headers.

- `--timeout`: request timeout in seconds.

- `--valid-accept-3xx`: treat any `< 400` response as acceptable for valid payloads

- `--fail-on-any/--no-fail-on-any`: exit non-zero if any case behaves unexpectedly

## Example Output
```
                                                             Schema Test Result
┏━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ record ┃ is_valid ┃ pass/fail ┃ status code ┃  time (ms) ┃ api response                                                                  ┃
┡━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ V000   │ yes      │ pass      │ 200         │        1.8 │ {"OK":true}                                                                   │
│ V001   │ yes      │ pass      │ 200         │        0.8 │ {"OK":true}                                                                   │
│ V002   │ yes      │ pass      │ 200         │        0.7 │ {"OK":true}                                                                   │
│ V003   │ yes      │ pass      │ 200         │        0.8 │ {"OK":true}                                                                   │
│ I026   │ no       │ fail      │ 422         │        0.5 │ {"detail":{"error":"invalid_email","message":"Email is not                    │
│        │          │           │             │            │ valid","field":"email"}}                                                      │
│ I027   │ no       │ fail      │ 422         │        0.6 │ {"detail":{"error":"invalid enum","message":"Schema validation                │
│        │          │           │             │            │ failed","details":"[\n  \"com.example.events.UserCreated.source is            │
│        │          │           │             │            │ <INVALID_SYMBOLS> of type <class 'str'> expected {'type': 'enum', 'name':     │
│        │          │           │             │            │ 'com.example.events.Source', 'symbols': ['web', 'mobile', 'api']}\"\n]"}}     │
│ I028   │ no       │ fail      │ 422         │        0.6 │ {"detail":{"error":"data type mismatch","message":"Schema validation          │
│        │          │           │             │            │ failed","details":"[\n  \"Field(com.example.events.UserCreated.id) is None    │
│        │          │           │             │            │ expected string\"\n]"}}                                                       │
│ I029   │ no       │ fail      │ 422         │        0.6 │ {"detail":{"error":"data type mismatch","message":"Schema validation          │
│        │          │           │             │            │ failed","details":"[\n  \"Field(com.example.events.UserCreated.tags) is None  │
│        │          │           │             │            │ expected {'type': 'array', 'items': 'string'}\"\n]"}}                         │
└────────┴──────────┴───────────┴─────────────┴────────────┴───────────────────────────────────────────────────────────────────────────────┘
Total: 8  Good: 4  Bad: 4

```
