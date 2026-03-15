import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Test: Health check
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# 2. Test: Create form successfully
def test_create_form():
    response = client.post(
        "/forms/",
        json={
            "title": "Test Form",
            "definition": {
                "type": "object",
                "properties": {"edad": {"type": "integer", "minimum": 18}},
                "required": ["edad"]
            }
        }
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Form"
    return response.json()["id"]

# 3. Test: Retrieve form by ID
def test_get_form():
    form_id = test_create_form()
    response = client.get(f"/forms/{form_id}")
    assert response.status_code == 200
    assert response.json()["id"] == form_id

# 4. Test: Get non-existent form
def test_get_nonexistent_form():
    response = client.get("/forms/99999")
    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]

# 5. Test: Submit valid data
def test_submit_valid_data():
    form_id = test_create_form()
    
    response = client.post(
        f"/forms/{form_id}/submit",
        json={"data": {"edad": 25}}
    )
    assert response.status_code == 200
    assert "Respuesta guardada" in response.json()["message"]

# 6. Test: Submit invalid data (wrong type)
def test_submit_invalid_data_type():
    form_id = test_create_form()
    response = client.post(
        f"/forms/{form_id}/submit",
        json={"data": {"edad": "bebe"}}
    )
    assert response.status_code == 400
    assert "Error de validación" in response.json()["detail"]

# 7. Test: Submit data that violates schema constraint
def test_submit_invalid_data_constraint():
    form_id = test_create_form()
    response = client.post(
        f"/forms/{form_id}/submit",
        json={"data": {"edad": 10}}  # Below minimum of 18
    )
    assert response.status_code == 400
    assert "Error de validación" in response.json()["detail"]

# 8. Test: Submit to non-existent form
def test_submit_to_nonexistent_form():
    response = client.post(
        "/forms/99999/submit",
        json={"data": {"edad": 25}}
    )
    assert response.status_code == 404
    assert "no encontrado" in response.json()["detail"]

# 9. Test: Get submissions for form
def test_get_submissions():
    form_id = test_create_form()
    
    # Submit valid data
    client.post(f"/forms/{form_id}/submit", json={"data": {"edad": 25}})
    client.post(f"/forms/{form_id}/submit", json={"data": {"edad": 30}})
    
    # Get submissions
    response = client.get(f"/forms/{form_id}/submissions")
    assert response.status_code == 200
    submissions = response.json()
    assert len(submissions) >= 2
