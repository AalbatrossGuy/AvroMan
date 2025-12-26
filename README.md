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
