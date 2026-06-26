import os
from celery import Celery
from app.pipeline import process_environmental_csv
from app.database import save_pipeline_output
# 1. Pull the Redis network URI from our environment variables
REDIS_URI = os.getenv("REDIS_URI", "redis://localhost:6373/0") 

# 2. Initialize the Celery Application Instance
celery_app = Celery(
    "data_cleaning_pipeline",
    broker=REDIS_URI,
    backend=REDIS_URI
)

# 3. Configure advanced Celery execution adjustments
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# 4. A dummy placeholder task to test our pipeline network later
@celery_app.task(name="test_worker_connection")
def test_worker_connection(x: int, y: int) -> int:
    return x + y


    """
  User clicks upload on the front-end.

FastAPI (web_app) receives the request, writes a task ticket, dumps it into Redis, and immediately tells the user: "Processing started!"

Redis (redis_broker) holds the ticket in line.

Celery (celery_worker) pulls the ticket out of Redis, loads Pandas, cleans the file, and writes the results to MongoDB.
    
    """
    
    




@celery_app.task(name="execute_data_pipeline_task")
def execute_data_pipeline_task(file_path: str, task_id: str) -> str:
    """Celery worker task that processes data and commits it to MongoDB."""
    # 1. Run the Pandas + Pydantic transformation loop
    pipeline_result = process_environmental_csv(file_path, task_id)
    
    # 2. Extract our structured dictionaries
    audit_report = pipeline_result["report"]
    clean_records = pipeline_result["clean_data"]
    
    # 3. Persist everything directly into MongoDB collections
    save_pipeline_output(audit_report, clean_records)
    
    return f"Task {task_id} successfully persisted to MongoDB."