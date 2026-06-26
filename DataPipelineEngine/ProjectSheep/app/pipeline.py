import pandas as pd
from datetime import datetime
from app.schemas import RawDataRow, PipelineAuditReport

def process_environmental_csv(file_path: str, task_id: str) -> dict:
    """
    Reads a messy CSV file, validates it row-by-row using Pydantic,
    tracks structural errors, and returns a clean MongoDB audit payload.
    """
    error_logs = []
    successful_rows = []
    corrupted_count = 0
    
    # 1. Read the raw file into Pandas
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {
            "task_id": task_id,
            "filename": file_path.split("/")[-1],
            "status": "FAILED",
            "error_logs": [{"row": "0", "error": f"Could not read CSV file: {str(e)}"}],
            "total_rows_read": 0,
            "successful_rows_saved": 0,
            "corrupted_rows_count": 0
        }

    total_rows = len(df)

    # 2. Iterate through each row and force it through Pydantic guardrails
    for index, row in df.iterrows():
        # Convert the Pandas row series into a standard Python dictionary
        raw_row_dict = row.to_dict()
        
        try:
            # Run data coercion and validation rules
            validated_row = RawDataRow.model_validate(raw_row_dict)
            
            # If successful, dump the clean object back to a dict for DB injection
            successful_rows.append(validated_row.model_dump())
            
        except Exception as err:
            # Capture the exact row number and validation error reason
            corrupted_count += 1
            error_logs.append({
                "row_index": str(index + 1),
                "error": str(err)
            })

    # 3. Compile the structural metadata report using our audit schema
    audit_report = PipelineAuditReport(
        task_id=task_id,
        filename=file_path.split("/")[-1],
        total_rows_read=total_rows,
        successful_rows_saved=len(successful_rows),
        corrupted_rows_count=corrupted_count,
        error_logs=error_logs,
        status="COMPLETED" if corrupted_count < total_rows else "FAILED"
    )

    # 4. Return standard dictionary ready for MongoDB or Celery backend delivery
    return {
        "report": audit_report.model_dump(),
        "clean_data": successful_rows
    }