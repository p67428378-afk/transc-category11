import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import CustomMapping
from schemas import CustomMappingCreate, CustomMappingUpdate

def test_create_custom_mapping(client: TestClient, session: Session):
    user_id = "test_user_1"
    new_mapping_data = {"merchant_keyword": "Starbucks", "category": "Coffee"}
    response = client.post(f"/api/v1/user/{user_id}/mappings", json=new_mapping_data)
    assert response.status_code == 201 # Changed from 200 to 201
    data = response.json()
    assert data["merchant_keyword"] == "Starbucks"
    assert data["category"] == "Coffee"
    assert data["user_id"] == user_id
    assert "custom_mapping_id" in data

    # Verify in DB
    db_mapping = session.query(CustomMapping).filter(CustomMapping.custom_mapping_id == data["custom_mapping_id"]).first()
    assert db_mapping is not None
    assert db_mapping.merchant_keyword == "Starbucks"

def test_create_custom_mapping_duplicate(client: TestClient, session: Session):
    user_id = "test_user_duplicate"
    # Create initial mapping
    initial_mapping_data = {"merchant_keyword": "DuplicateMerchant", "category": "Category1"}
    response = client.post(f"/api/v1/user/{user_id}/mappings", json=initial_mapping_data)
    assert response.status_code == 201

    # Attempt to create duplicate mapping
    duplicate_mapping_data = {"merchant_keyword": "DuplicateMerchant", "category": "Category2"}
    response = client.post(f"/api/v1/user/{user_id}/mappings", json=duplicate_mapping_data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_create_custom_mapping_invalid_input_empty(client: TestClient):
    user_id = "test_user_invalid_empty"
    invalid_mapping_data = {"merchant_keyword": "", "category": "Category"}
    response = client.post(f"/api/v1/user/{user_id}/mappings", json=invalid_mapping_data)
    assert response.status_code == 422
    # Assert that there's a validation error detail in the response
    assert "detail" in response.json()
    assert len(response.json()["detail"]) > 0

    invalid_mapping_data = {"merchant_keyword": "Merchant", "category": ""}
    response = client.post(f"/api/v1/user/{user_id}/mappings", json=invalid_mapping_data)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) > 0

def test_create_custom_mapping_invalid_input_too_long(client: TestClient):
    user_id = "test_user_invalid_long"
    long_string = "a" * 256 # Exceeds max_length=255
    invalid_mapping_data = {"merchant_keyword": long_string, "category": "Category"}
    response = client.post(f"/api/v1/user/{user_id}/mappings", json=invalid_mapping_data)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) > 0

    invalid_mapping_data = {"merchant_keyword": "Merchant", "category": long_string}
    response = client.post(f"/api/v1/user/{user_id}/mappings", json=invalid_mapping_data)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert len(response.json()["detail"]) > 0

def test_get_custom_mappings_for_user(client: TestClient, session: Session):
    user_id = "test_user_2"
    mapping1 = CustomMapping(user_id=user_id, merchant_keyword="Netflix", category="Entertainment")
    mapping2 = CustomMapping(user_id=user_id, merchant_keyword="Spotify", category="Music")
    session.add_all([mapping1, mapping2])
    session.commit()
    session.refresh(mapping1)
    session.refresh(mapping2)

    response = client.get(f"/api/v1/user/{user_id}/mappings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(m["merchant_keyword"] == "Netflix" for m in data)
    assert any(m["merchant_keyword"] == "Spotify" for m in data)

def test_get_single_custom_mapping(client: TestClient, session: Session):
    user_id = "test_user_3"
    mapping = CustomMapping(user_id=user_id, merchant_keyword="Amazon", category="Shopping")
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    response = client.get(f"/api/v1/user/{user_id}/mappings/{mapping.custom_mapping_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_keyword"] == "Amazon"
    assert data["category"] == "Shopping"

def test_update_custom_mapping(client: TestClient, session: Session):
    user_id = "test_user_4"
    mapping = CustomMapping(user_id=user_id, merchant_keyword="Old Keyword", category="Old Category")
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    update_data = {"merchant_keyword": "New Keyword", "category": "New Category"}
    response = client.put(f"/api/v1/user/{user_id}/mappings/{mapping.custom_mapping_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_keyword"] == "New Keyword"
    assert data["category"] == "New Category"

    # Verify in DB
    session.refresh(mapping)
    assert mapping.merchant_keyword == "New Keyword"
    assert mapping.category == "New Category"

def test_update_custom_mapping_duplicate_conflict(client: TestClient, session: Session):
    user_id = "test_user_update_conflict"
    # Create two initial mappings
    mapping1 = CustomMapping(user_id=user_id, merchant_keyword="KeywordA", category="CategoryA")
    mapping2 = CustomMapping(user_id=user_id, merchant_keyword="KeywordB", category="CategoryB")
    session.add_all([mapping1, mapping2])
    session.commit()
    session.refresh(mapping1)
    session.refresh(mapping2)

    # Attempt to update mapping1 to have the same merchant_keyword as mapping2
    update_data = {"merchant_keyword": "KeywordB"}
    response = client.put(f"/api/v1/user/{user_id}/mappings/{mapping1.custom_mapping_id}", json=update_data)
    assert response.status_code == 400
    assert "Update would create a duplicate custom mapping" in response.json()["detail"]

def test_partial_update_custom_mapping(client: TestClient, session: Session):
    user_id = "test_user_5"
    mapping = CustomMapping(user_id=user_id, merchant_keyword="Partial Old", category="Partial Category")
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    update_data = {"category": "Updated Partial Category"}
    response = client.put(f"/api/v1/user/{user_id}/mappings/{mapping.custom_mapping_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_keyword"] == "Partial Old"
    assert data["category"] == "Updated Partial Category"

    # Verify in DB
    session.refresh(mapping)
    assert mapping.merchant_keyword == "Partial Old"
    assert mapping.category == "Updated Partial Category"

def test_delete_custom_mapping(client: TestClient, session: Session):
    user_id = "test_user_6"
    mapping = CustomMapping(user_id=user_id, merchant_keyword="To Delete", category="Delete Category")
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    response = client.delete(f"/api/v1/user/{user_id}/mappings/{mapping.custom_mapping_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Custom mapping deleted successfully"}

    # Verify in DB
    db_mapping = session.query(CustomMapping).filter(CustomMapping.custom_mapping_id == mapping.custom_mapping_id).first()
    assert db_mapping is None
