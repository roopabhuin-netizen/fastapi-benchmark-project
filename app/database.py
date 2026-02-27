from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.mongodb_url)
db = client[settings.database_name]

db["executions"].create_index("benchmark_id")
db["executions"].create_index("executed_at")
db["metrics"].create_index("execution_id")