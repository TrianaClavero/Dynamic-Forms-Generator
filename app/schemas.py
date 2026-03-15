from pydantic import BaseModel, Field
from typing import Dict, Any
from datetime import datetime

class FormSubmissionCreate(BaseModel):
    data: Dict[str, Any] = Field(..., description="Form submission data")

class FormSubmissionResponse(BaseModel):
    id: int
    form_id: int
    data_json: Dict[str, Any]
    submitted_at: datetime

    class Config:
        from_attributes = True

class FormCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Form title")
    definition: Dict[str, Any] = Field(..., description="JSON Schema for form validation")
    description: str | None = Field(None, max_length=500, description="Form description")

class FormResponse(BaseModel):
    id: int
    title: str
    description: str | None
    definition: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class ErrorResponse(BaseModel):
    detail: str
