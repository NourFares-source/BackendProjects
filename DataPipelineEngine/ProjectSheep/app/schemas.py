from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from datetime import datetime

class RawDataRow(BaseModel):
    """Validates an incoming single row from the messy CSV file."""
    timestamp: str
    location: str = Field(..., min_length=2)
    aqi_value: Optional[float] = None  # Can be empty or missing in messy data
    traffic_density: Optional[float] = None
    sensor_status: str = "Active"

    @field_validator('aqi_value', 'traffic_density')
    @classmethod
    def check_negative_values(cls, v):
        if v is not None and v < 0:
            raise ValueError("Metrics cannot be negative numerical values")
        return v     

class PipelineAuditReport(BaseModel):
    """Schema for the final quality report stored in MongoDB."""
    task_id: str
    filename: str
    processed_at: datetime = Field(default_factory=datetime.now)
    total_rows_read: int
    successful_rows_saved: int
    corrupted_rows_count: int
    error_logs: List[Dict[str, str]]  # Stores exactly which rows failed and why
    status: str = "COMPLETED"