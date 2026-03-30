from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.models import CustomMapping
from backend.schemas import CustomMappingCreate

def test_create_custom_mapping(client: TestClient, session: Session):
    user_id = "test_user_1"
    mapping_data = {"merchant_keyword": "Local Cafe", "category": "Dining"}
    response = client.post(f"/api/v1/users/{user_id}/mappings", json=mapping_data)
    assert response.status_code == 201 # Changed from 200 to 201
    data = response.json()
    assert data["merchant_keyword"] == "Local Cafe"
    assert data["category"] == "Dining"
    assert data["user_id"] == user_id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify in database
    db_mapping = session.query(CustomMapping).filter(CustomMapping.id == data["id"]).first()
    assert db_mapping is not None
    assert db_mapping.merchant_keyword == "Local Cafe"
    assert db_mapping.category == "Dining"
    assert db_mapping.user_id == user_id

def test_create_custom_mapping_duplicate(client: TestClient, session: Session):
    user_id = "test_user_2"
    mapping_data = {"merchant_keyword": "Duplicate Store", "category": "Category A"}
    client.post(f"/api/v1/users/{user_id}/mappings", json=mapping_data)
    response = client.post(f"/api/v1/users/{user_id}/mappings", json=mapping_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_create_custom_mapping_invalid_input(client: TestClient):
    user_id = "test_user_3"
    invalid_mapping_data = {"merchant_keyword": "", "category": "Dining"}
    response = client.post(f"/api/v1/users/{user_id}/mappings", json=invalid_mapping_data)
    assert response.status_code == 422 # Unprocessable Entity for validation errors

    invalid_mapping_data = {"merchant_keyword": "Valid", "category": ""}
    response = client.post(f"/api/v1/users/{user_id}/mappings", json=invalid_mapping_data)
    assert response.status_code == 422

def test_get_custom_mappings(client: TestClient, session: Session):
    user_id = "test_user_4"
    mapping_data_1 = {"merchant_keyword": "Store A", "category": "Category A"}
    mapping_data_2 = {"merchant_keyword": "Store B", "category": "Category B"}
    client.post(f"/api/v1/users/{user_id}/mappings", json=mapping_data_1)
    client.post(f"/api/v1/users/{user_id}/mappings", json=mapping_data_2)

    response = client.get(f"/api/v1/users/{user_id}/mappings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(m["merchant_keyword"] == "Store A" for m in data)
    assert any(m["merchant_keyword"] == "Store B" for m in data)

def test_get_custom_mapping_by_id(client: TestClient, session: Session):
    user_id = "test_user_5"
    mapping_data = {"merchant_keyword": "Specific Store", "category": "Specific Category"}
    post_response = client.post(f"/api/v1/users/{user_id}/mappings", json=mapping_data)
    mapping_id = post_response.json()["id"]

    get_response = client.get(f"/api/v1/users/{user_id}/mappings/{mapping_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["merchant_keyword"] == "Specific Store"
    assert data["category"] == "Specific Category"
    assert data["user_id"] == user_id

def test_get_custom_mapping_not_found(client: TestClient):
    user_id = "test_user_6"
    response = client.get(f"/api/v1/users/{user_id}/mappings/99999")
    assert response.status_code == 404
    assert "Mapping not found" in response.json()["detail"]

def test_update_custom_mapping(client: TestClient, session: Session):
    user_id = "test_user_7"
    mapping_data = {"merchant_keyword": "Old Keyword", "category": "Old Category"}
    post_response = client.post(f"/api/v1/users/{user_id}/mappings", json=mapping_data)
    mapping_id = post_response.json()["id"]

    update_data = {"merchant_keyword": "New Keyword", "category": "New Category"}
    update_response = client.put(f"/api/v1/users/{user_id}/mappings/{mapping_id}", json=update_data)
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["merchant_keyword"] == "New Keyword"
    assert data["category"] == "New Category"
    assert data["user_id"] == user_id

    # Verify in database
    db_mapping = session.query(CustomMapping).filter(CustomMapping.id == mapping_id).first()
    assert db_mapping.merchant_keyword == "New Keyword"
    assert db_mapping.category == "New Category"

def test_update_custom_mapping_not_found(client: TestClient):
    user_id = "test_user_8"
    update_data = {"merchant_keyword": "NonExistent", "category": "Category"}
    response = client.put(f"/api/v1/users/{user_id}/mappings/99999", json=update_data)
    assert response.status_code == 404
    assert "Mapping not found" in response.json()["detail"]

def test_update_custom_mapping_unauthorized_user(client: TestClient, session: Session):
    user_id_1 = "user_a"
    user_id_2 = "user_b"
    mapping_data = {"merchant_keyword": "Shared Store", "category": "Shared Category"}
    post_response = client.post(f"/api/v1/users/{user_id_1}/mappings", json=mapping_data)
    mapping_id = post_response.json()["id"]

    update_data = {"merchant_keyword": "Attempted Change", "category": "Attempted Category"}
    response = client.put(f"/api/v1/users/{user_id_2}/mappings/{mapping_id}", json=update_data)
    assert response.status_code == 404 # Or 403 Forbidden, depending on exact auth implementation
    assert "Mapping not found" in response.json()["detail"]

def test_delete_custom_mapping(client: TestClient, session: Session):
    user_id = "test_user_9"
    mapping_data = {"merchant_keyword": "To Be Deleted", "category": "Delete Category"}
    post_response = client.post(f"/api/v1/users/{user_id}/mappings", json=mapping_data)
    mapping_id = post_response.json()["id"]

    delete_response = client.delete(f"/api/v1/users/{user_id}/mappings/{mapping_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Mapping deleted successfully"

    # Verify in database
    db_mapping = session.query(CustomMapping).filter(CustomMapping.id == mapping_id).first()
    assert db_mapping is None

def test_delete_custom_mapping_not_found(client: TestClient):
    user_id = "test_user_10"
    response = client.delete(f"/api/v1/users/{user_id}/mappings/99999")
    assert response.status_code == 404
    assert "Mapping not found" in response.json()["detail"]

def test_delete_custom_mapping_unauthorized_user(client: TestClient, session: Session):
    user_id_1 = "user_c"
    user_id_2 = "user_d"
    mapping_data = {"merchant_keyword": "Another Shared Store", "category": "Another Shared Category"}
    post_response = client.post(f"/api/v1/users/{user_id_1}/mappings", json=mapping_data)
    mapping_id = post_response.json()["id"]

    response = client.delete(f"/api/v1/users/{user_id_2}/mappings/{mapping_id}")
    assert response.status_code == 404 # Or 403 Forbidden
    assert "Mapping not found" in response.json()["detail"]
