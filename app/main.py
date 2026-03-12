from time import time

from fastapi import FastAPI, HTTPException, Depends
from jsonschema import validate, ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from . import models, database
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

def create_tables():
    retries = 5
    while retries > 0:
        try:
            models.Base.metadata.create_all(bind=engine)
            print("Tablas creadas exitosamente")
            break
        except OperationalError:
            retries -= 1
            print(f"Esperando a la DB... reintentos restantes: {retries}")
            time.sleep(2)

create_tables()

app = FastAPI(
    title="Motor de Formularios Dinámicos",
    description="API robusta para la creación, gestión y validación de formularios dinámicos usando JSON Schema.",
    version="1.0.0",
    contact={
        "name": "Triana Clavero",
        "url": "https://github.com/TrianaClavero",
    },
)

@app.get("/")
def read_root():
    return {"status": "Backend de Formularios Dinámicos Activo"}

@app.post("/forms/{form_id}/submit")
def submit_form(form_id: int, data: dict, db: Session = Depends(get_db)):
    form = db.query(models.FormDefinition).filter(models.FormDefinition.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulario no encontrado")

    try:
        validate(instance=data, schema=form.schema_json)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Error de validación: {e.message}")

    new_submission = models.FormSubmission(form_id=form_id, data_json=data)
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    return {"message": "Respuesta guardada con éxito", "id": new_submission.id}

@app.post("/forms/")
def create_form(title: str, schema: dict, db: Session = Depends(database.get_db)):
    new_form = models.FormDefinition(title=title, schema_json=schema)
    db.add(new_form)
    db.commit()
    db.refresh(new_form)
    return new_form

def get_form_from_db(form_id: int):
    db = next(database.get_db())
    form = db.query(models.FormDefinition).filter(models.FormDefinition.id == form_id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulario no encontrado")
    return form

def save_submission(form_id: int, data: dict):
    db = next(database.get_db())
    submission = models.FormSubmission(form_id=form_id, data_json=data)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission