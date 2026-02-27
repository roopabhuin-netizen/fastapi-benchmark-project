from fastapi import APIRouter
from app.database import db

router = APIRouter()

@router.get("/health")
def health_check():
    try:
        db.command("ping")
        return {"status": "UP", "database": "Connected"}
    except Exception:
        return {"status": "DOWN", "database": "Disconnected"}
        



