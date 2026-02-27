from fastapi import FastAPI,Request
from app.routers import health,benchmark_route,auth,execution_route,regression
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.get("/")
def home():
    return {"message": "MongoDB connected successfully"}



app.include_router(health.router)
app.include_router(benchmark_route.router)
app.include_router(auth.router)
app.include_router(execution_route.router)
app.include_router(regression.router)
