# Distributed Data Ingestion & Automated Cleaning Pipeline

A high-performance, asynchronous data processing pipeline built from scratch to clean, validate, and persist messy environmental sensor data. This project demonstrates a decoupled microservices architecture designed to offload long-running computational tasks from the web server layer to scalable background workers.

## 🏗️ Architecture Overview

The system is fully containerized using Docker and separated into four core services:

1. **FastAPI Gateway Layer (`web_app`)**: A high-speed, non-blocking HTTP API engine that manages file uploads and quickly drops work tokens onto the message broker, providing sub-second client response times.
2. **Redis Message Broker (`redis_broker`)**: An ultra-fast, in-memory data store acting as the thread-safe message queue between the API and the background workers.
3. **Celery Distributed Worker (`celery_worker`)**: An isolated background worker engine that pulls task tickets sequentially from Redis and executes heavy computational logic.
4. **Pandas & Pydantic Processing Engine (`pipeline.py`)**: The data core. Loads unstructured chunked datasets using Pandas, enforces strict typing/data guardrails via Pydantic schemas, logs row-level structural error telemetry, and generates operational audit footprints.
5. **MongoDB NoSQL Persistence (`mongodb`)**: Stores structural operational audit logs and sanitized data streams into separate document collections for future analytics.

## 🚀 Key Engineering Skills Demonstrated
* **Asynchronous Offloading**: Offloading multi-megabyte dataset parsing safely away from the HTTP application thread using the Worker-Broker pattern.
* **Shared Persistent Volumes**: Orchestrating multi-container data sharing using unified Docker storage volumes so files never load into server memory twice.
* **Data Guardrails & Sanitization**: Catching corrupted values (e.g., structural mismatches, faulty metrics) row-by-row inside a data loop without crashing the runtime worker.
* **Infrastructure Orchestration**: Wiring up a multi-service network ecosystem with complex port configurations using single-command Docker Compose environments.

---

## 📂 Project Repository Structure

```text
DataPipelineEngine/
├── app/
│   ├── templates/
│   │   └── index.html      # Bootstrap Async Dashboard UI
│   ├── __init__.py
│   ├── database.py         # PyMongo Connection Pooling
│   ├── main.py             # FastAPI App Gateway & HTML Routers
│   ├── pipeline.py         # Core Pandas + Pydantic Processing Engine
│   ├── schemas.py          # Data Validation Contracts
│   └── worker.py           # Celery Task Configurations
├── docker-compose.yml       # Cluster Orchestration Blueprint
├── Dockerfile              # Python Environment Blueprint
└── requirements.txt        # Managed Application Dependencies
