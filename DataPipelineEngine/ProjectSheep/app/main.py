from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
import uuid
import os
from app.worker import celery_app

app = FastAPI(title="Distributed Data Pipeline Engine")

# Define where we will temporarily store uploaded files inside the shared volume
SHARED_STORAGE_DIR = "/code/shared_storage"
TEMPLATES_DIR = "/code/app/templates"

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the visual file submission interface."""
    html_path = os.path.join(TEMPLATES_DIR, "index.html")
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="Frontend template missing.")
        
    with open(html_path, "r") as file:
        return file.read()
@app.post("/api/v1/pipeline/upload")
async def upload_pipeline_file(file: UploadFile = File(...)):
    """
    Accepts a raw CSV file upload, saves it to the shared volume,
    and dispatches a background processing task to Celery via Redis.
    """
    # 1. Guardrail: Enforce that only CSV files can be submitted
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are supported.")

    # 2. Generate secure unique identifiers
    task_id = str(uuid.uuid4())
    secure_filename = f"{task_id}_{file.filename}"
    local_target_path = os.path.join(SHARED_STORAGE_DIR, secure_filename)

    # 3. Stream the uploaded bytes directly into our shared volume desk drawer
    try:
        os.makedirs(SHARED_STORAGE_DIR, exist_ok=True)
        with open(local_target_path, "wb") as buffer:
            # Read file payload in chunks to avoid overwhelming server memory
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write file to storage disk: {str(e)}")

    # 4. Dispatch the job ticket over the Redis highway to Celery
    # .send_task tells Celery to run the worker function matching this string name
    celery_app.send_task(
        "execute_data_pipeline_task",
        args=[local_target_path, task_id]
    )

    # 5. Instantly respond to the user with their tracking ID
    return {
        "status": "QUEUED",
        "message": "File uploaded successfully. Data scrubbing is processing asynchronously.",
        "task_id": task_id,
        "file_tracked": secure_filename
    }