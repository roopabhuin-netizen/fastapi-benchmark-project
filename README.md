#  Benchmark Performance Tracking System

A FastAPI-based backend system for managing benchmark definitions,
uploading execution results, comparing performance runs, and
automatically detecting regressions using rule-based logic.

------------------------------------------------------------------------

##  Features

-   JWT Authentication
-   Benchmark Registration
-   Execution Upload
-   Execution History with Filtering & Sorting
-   Performance Comparison Between Runs
-   Automatic Regression Detection
-   Normalized MongoDB Schema Design

------------------------------------------------------------------------

##  Architecture Overview

The system follows a normalized 3-collection MongoDB schema:

Benchmarks (1) → Executions (Many) → Metrics (Many per execution)

### Collections

-   benchmarks → Stores benchmark definitions & metric rules
-   executions → Stores individual benchmark runs
-   metrics → Stores metric values per execution

### Relationships

-   executions.benchmark_id → benchmarks.\_id
-   metrics.execution_id → executions.\_id

------------------------------------------------------------------------

##  Tech Stack

-   Backend: FastAPI
-   Database: MongoDB
-   Authentication: JWT
-   Validation: Pydantic
-   Server: Uvicorn

------------------------------------------------------------------------

##  API Endpoints

### Authentication

POST /login

### Benchmark Registration

POST /benchmarks\
GET /benchmarks

### Upload Execution

POST /executions/upload

### Get Execution Details

GET /executions/{execution_id}

### Compare Executions

GET /executions/compare?base=`<id>`{=html}&target=`<id>`{=html}

Formula: Percent Change = (Target - Base) / Base × 100

### Regression Detection

GET /regression?base=`<id>`{=html}&target=`<id>`{=html}

### Historical Query

GET /benchmarks/{benchmark_name}/history

Supports optional filters: cpu_model, cores, git_commit, limit, sort,
order

------------------------------------------------------------------------

##  Installation

1.  Clone repository
2.  Create virtual environment
3.  Install dependencies
4.  Configure .env file
5.  Run: uvicorn app.main:app --reload

Swagger UI: http://127.0.0.1:8000/docs

------------------------------------------------------------------------

## Real-World Use Case

Simulates CI/CD performance validation and regression detection
workflows.


------------------------------------------------------------------------

Benchmark Performance Tracking & Regression Detection System built using
FastAPI and MongoDB.
