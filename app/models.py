from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .database import Base

class FormDefinition(Base):
    __tablename__ = "form_definitions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    schema_json = Column(JSONB, nullable=False) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("form_definitions.id"))
    data_json = Column(JSONB, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())