from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from bson import ObjectId
from app.database import db
from app.models.execution_model import ExecutionCreate
from app.core.security import verify_token


router = APIRouter(prefix="/executions", tags=["Executions"])
@router.post("/upload")
def upload_execution(
    payload: ExecutionCreate,                 
    token_data: dict = Depends(verify_token)  # JWT authentication dependency
):

    # Check if the benchmark exists in the database
    benchmark = db["benchmarks"].find_one(
        {"name": payload.benchmark_name}
    )

    if not benchmark:
        raise HTTPException(status_code=400, detail="Benchmark not found")

    execution_doc = {
        "benchmark_id": benchmark["_id"],             
        "git_commit": payload.git_commit,             
        "system_config": payload.system_config.dict(),
        "executed_at": datetime.utcnow(),             
        "uploaded_by": token_data.get("sub")          
    }

    # Insert execution_doc into "executions" collection
    execution_result = db["executions"].insert_one(execution_doc)
    execution_id = execution_result.inserted_id

    # Get metric rules defined for this benchmark
    metric_rules = benchmark.get("metric_rules", {})

    for metric_name, metric_value in payload.metrics.items():
        if metric_name not in metric_rules:
            raise HTTPException(
                status_code=400,
                detail=f"Metric '{metric_name}' not defined in benchmark"
            )

        # Get unit from metric rules
        unit = metric_rules[metric_name]["unit"]

        metric_doc = {
            "execution_id": execution_id,   # Link to execution
            "metric_name": metric_name,     
            "metric_value": metric_value,   
            "unit": unit                    
        }
        db["metrics"].insert_one(metric_doc)

    return {
        "message": "Execution uploaded successfully",
        "execution_id": str(execution_id)
    }



#  Compare Two Executions API

@router.get("/compare")
def compare_executions(
    base: str,                                # Base execution ID
    target: str,                              # Target execution ID
    token_data: dict = Depends(verify_token)  # JWT authentication
):

    # Validate ObjectId format
    if not ObjectId.is_valid(base) or not ObjectId.is_valid(target):
        raise HTTPException(status_code=400, detail="Invalid execution ID format")

    # Convert string IDs to ObjectId
    base_id = ObjectId(base)
    target_id = ObjectId(target)

    # Fetch execution documents
    base_execution = db["executions"].find_one({"_id": base_id})
    target_execution = db["executions"].find_one({"_id": target_id})

    # Check if executions exist
    if not base_execution or not target_execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    # check both executions belong to same benchmark
    if base_execution["benchmark_id"] != target_execution["benchmark_id"]:
        raise HTTPException(
            status_code=400,
            detail="Executions belong to different benchmarks"
        )

    # Fetch metrics for both executions
    base_metrics_cursor = db["metrics"].find({"execution_id": base_id})
    target_metrics_cursor = db["metrics"].find({"execution_id": target_id})

    # Convert metrics into dictionary format
    base_metrics = {
        m["metric_name"]: m["metric_value"]
        for m in base_metrics_cursor
    }

    target_metrics = {
        m["metric_name"]: m["metric_value"]
        for m in target_metrics_cursor
    }

    # comparison result dictionary
    comparison = {}

    # Compare each metric
    for metric in base_metrics:

        if metric not in target_metrics:
            continue
        base_value = float(base_metrics[metric])
        target_value = float(target_metrics[metric])
        if base_value == 0:
            percent_change = 0.0
        else:
            percent_change = ((target_value - base_value) / base_value) * 100

        # Store comparison result
        comparison[metric] = {
            "base": base_value,
            "target": target_value,
            "percent_change": f"{round(percent_change, 2)}%"
        }

    # Fetch benchmark name
    benchmark = db["benchmarks"].find_one(
        {"_id": base_execution["benchmark_id"]}
    )

    benchmark_name = benchmark["name"] if benchmark else None
    return {
        "benchmark": benchmark_name,
        "base_execution": base,
        "target_execution": target,
        "comparison": comparison
    }



#  Get Execution Details 

@router.get("/{execution_id}")
def get_execution_details(
    execution_id: str,
    token_data: dict = Depends(verify_token)  # JWT authentication
):

    # Validate ObjectId format
    if not ObjectId.is_valid(execution_id):
        raise HTTPException(status_code=400, detail="Invalid execution ID format")

    # Fetch execution document
    execution = db["executions"].find_one(
        {"_id": ObjectId(execution_id)}
    )
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    # Fetch related benchmark
    benchmark = db["benchmarks"].find_one(
        {"_id": execution.get("benchmark_id")}
    )
    benchmark_name = benchmark["name"] if benchmark else None

    # Fetch all metrics for this execution
    metrics_cursor = db["metrics"].find(
        {"execution_id": ObjectId(execution_id)}
    )

    metrics_dict = {}

    # Convert metrics into dictionary format
    for metric in metrics_cursor:
        metrics_dict[metric["metric_name"]] = {
            "value": metric["metric_value"],
            "unit": metric["unit"]
        }


    response = {
        "execution_id": str(execution["_id"]),
        "benchmark_name": benchmark_name,
        "git_commit": execution.get("git_commit"),
        "system_config": execution.get("system_config"),
        "executed_at": execution.get("executed_at"),
        "uploaded_by": execution.get("uploaded_by"),
        "metrics": metrics_dict
    }

    return response


