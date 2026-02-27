from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.database import db
from app.core.security import verify_token

router = APIRouter(prefix="/regression", tags=["Regression"])


#regression detection endpoint
@router.get("/")
def detect_regression(
    base: str,                                 # Base execution ID
    target: str,                               # Target execution ID
    token_data: dict = Depends(verify_token)   # JWT authentication
):

    if not ObjectId.is_valid(base) or not ObjectId.is_valid(target):
        raise HTTPException(status_code=400, detail="Invalid execution ID format")

    # Convert string IDs to MongoDB ObjectId
    base_id = ObjectId(base)
    target_id = ObjectId(target)


    #  Fetch execution documents from database
    base_execution = db["executions"].find_one({"_id": base_id})
    target_execution = db["executions"].find_one({"_id": target_id})

    if not base_execution or not target_execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    # check both executions belong to the same benchmark
    if base_execution["benchmark_id"] != target_execution["benchmark_id"]:
        raise HTTPException(
            status_code=400,
            detail="Executions belong to different benchmarks"
        )


    benchmark = db["benchmarks"].find_one(
        {"_id": base_execution["benchmark_id"]}
    )

    if not benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")

    metric_rules = benchmark.get("metric_rules", {})

    base_metrics = {
        m["metric_name"]: m["metric_value"]
        for m in db["metrics"].find({"execution_id": base_id})
    }

    target_metrics = {
        m["metric_name"]: m["metric_value"]
        for m in db["metrics"].find({"execution_id": target_id})
    }
    results = {}
    regression_detected = False


    #  Compare each metric 
    for metric in base_metrics:

        # Skip if metric not present in target execution
        if metric not in target_metrics:
            continue

        if metric not in metric_rules:
            continue


        base_value = float(base_metrics[metric])
        target_value = float(target_metrics[metric])

        if base_value == 0:
            continue


        percent_change = ((target_value - base_value) / base_value) * 100
        percent_change = round(percent_change, 2)

        rule = metric_rules[metric]
        better = rule.get("better")                     # "higher" or "lower"
        tolerance = rule.get("tolerance_percent", 5)   # Default tolerance = 5%

        status = "OK"


        # Case 1: Higher value is better
        if better == "higher":
            # If performance decreased more than tolerance → Regression
            if percent_change < -tolerance:
                status = "REGRESSION"
                regression_detected = True

        # Case 2: Lower value is better
        elif better == "lower":
            # If performance increased more than tolerance → Regression
            if percent_change > tolerance:
                status = "REGRESSION"
                regression_detected = True

        # Store result for this metric
        results[metric] = {
            "percent_change": percent_change,
            "status": status
        }


    return {
        "benchmark": benchmark["name"],            # Benchmark name
        "regression_detected": regression_detected, # True if any metric regressed
        "metrics": results                          # Detailed metric-wise results
    }
