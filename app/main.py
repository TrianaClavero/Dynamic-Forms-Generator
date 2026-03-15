import os
import time
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jsonschema import validate, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from . import models, schemas
from .database import engine, get_db

# Initialize database with retry logic
def init_db():
    """Initialize database with retry pattern for container startup"""
    retries = 20
    while retries > 0:
        try:
            models.Base.metadata.create_all(bind=engine)
            print("✅ Database tables created successfully")
            return
        except OperationalError as e:
            retries -= 1
            wait_time = 2
            print(f"⏳ Waiting for DB... retries left: {retries} - {e}")
            time.sleep(wait_time)
    
    raise RuntimeError("Failed to connect to database after retries")

init_db()

app = FastAPI(
    title="Motor de Formularios Dinámicos",
    description="API robusta para la creación, gestión y validación de formularios dinámicos usando JSON Schema.",
    version="1.0.0",
    contact={
        "name": "Triana Clavero",
        "url": "https://github.com/TrianaClavero",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.post("/forms/", response_model=schemas.FormResponse, tags=["Forms"], status_code=status.HTTP_201_CREATED)
def create_form(
    form_data: schemas.FormCreateRequest, 
    db: Session = Depends(get_db)
):
    """Create a new dynamic form with JSON Schema definition"""
    try:
        new_form = models.FormDefinition(
            title=form_data.title,
            description=form_data.description,
            definition=form_data.definition
        )
        db.add(new_form)
        db.commit()
        db.refresh(new_form)
        return new_form
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create form: {str(e)}"
        )

@app.get("/forms/{form_id}", response_model=schemas.FormResponse, tags=["Forms"])
def get_form(form_id: int, db: Session = Depends(get_db)):
    """Retrieve a form definition by ID"""
    form = db.query(models.FormDefinition).filter(models.FormDefinition.id == form_id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formulario no encontrado")
    return form

@app.post("/forms/{form_id}/submit", tags=["Submissions"], status_code=status.HTTP_200_OK)
def submit_form(
    form_id: int,
    submission: schemas.FormSubmissionCreate,
    db: Session = Depends(get_db)
):
    """Submit form data for validation against form schema"""
    # Verify form exists
    form = db.query(models.FormDefinition).filter(models.FormDefinition.id == form_id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formulario no encontrado")

    # Validate submission against schema
    try:
        validate(instance=submission.data, schema=form.definition)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación: {e.message}"
        )

    # Save submission
    try:
        new_submission = models.FormSubmission(form_id=form_id, data_json=submission.data)
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)
        return {
            "id": new_submission.id,
            "message": "Respuesta guardada con éxito",
            "submitted_at": new_submission.submitted_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save submission: {str(e)}"
        )

@app.get("/forms/{form_id}/submissions", tags=["Submissions"])
def get_submissions(form_id: int, db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    """Retrieve all submissions for a specific form"""
    form = db.query(models.FormDefinition).filter(models.FormDefinition.id == form_id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Formulario no encontrado")
    
    submissions = db.query(models.FormSubmission).filter(
        models.FormSubmission.form_id == form_id
    ).offset(skip).limit(limit).all()
    
    return submissions
