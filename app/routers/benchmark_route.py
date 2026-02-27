from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from app.database import db
from app.models.benchmark_model import BenchmarkCreate
from app.core.security import verify_token

router = APIRouter(prefix="/benchmarks", tags=["Benchmarks"])

@router.post("/")
def create_benchmark(
    benchmark: BenchmarkCreate,
    token_data: dict = Depends(verify_token)
):

    existing = db["benchmarks"].find_one({"name": benchmark.name})
    if existing:
        raise HTTPException(status_code=400, detail="Benchmark already exists")

    benchmark = {
        "name": benchmark.name,
        "display_name": benchmark.display_name,
        "category": benchmark.category,
        "description": benchmark.description,
        "metric_rules": {
            metric: rule.dict()
            for metric, rule in benchmark.metric_rules.items()
        },
        "created_by": benchmark.created_by,  
        "created_at": datetime.utcnow()
    }

    result = db["benchmarks"].insert_one(benchmark)

    return {
        "message": "Benchmark created successfully",
        "id": str(result.inserted_id)
    }


@router.get("/")
def list_benchmarks():
    benchmarks = list(db["benchmarks"].find({}))
    for benchmark in benchmarks:
        benchmark["_id"]=str(benchmark["_id"])
    return benchmarks


@router.get("/{benchmark_name}/history")
def get_benchmark_history(
    benchmark_name: str,
    cpu_model: str | None = None,
    cores: int | None = None,           #Query parameters
    git_commit: str | None = None,
    limit: int = 20,
    sort: str = "executed_at",
    order: str = "desc",
    token_data: dict = Depends(verify_token)
):
    
    # Step 1 — Validate Benchmark
    benchmark = db["benchmarks"].find_one({"name": benchmark_name})
    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    benchmark_id = benchmark["_id"]

    # Step 2 — Build Dynamic Query
    query = {
        "benchmark_id": benchmark_id
    }

    if cpu_model:
        query["system_config.cpu"] = cpu_model

    if cores:
        query["system_config.cores"] = cores

    if git_commit:
        query["git_commit"] = git_commit

    # Step 3 — Sorting & Limiting

    allowed_sort_fields = ["executed_at"]

    if sort not in allowed_sort_fields:
       sort = "executed_at"

    sort_direction = -1 if order == "desc" else 1

    cursor = (
        db["executions"]
        .find(query)
        .sort([(sort, sort_direction)]) 
        .limit(limit)
    )

    executions_list = []

    for execution in cursor:
        executions_list.append({
            "execution_id": str(execution["_id"]),
            "git_commit": execution.get("git_commit"),
            "system_config": execution.get("system_config"),
            "executed_at": execution.get("executed_at"),
            "uploaded_by": execution.get("uploaded_by")
        })

    # Step 4 — Return Response
    return {
        "benchmark": benchmark_name,
        "total_results": len(executions_list),
        "executions": executions_list
    }