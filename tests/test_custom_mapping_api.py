import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import CustomMapping
from schemas import CustomMappingCreate, CustomMappingUpdate

def test_create_custom_mapping(client: TestClient, session: Session):
    user_id = "test_user_1"
    new_mapping_data = {"merchant_keyword": "Starbucks", "category": "Coffee"}
    response = client.post(f"/api/v1/user/{user_id}/mappings", json=new_mapping_data)
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_keyword"] == "Starbucks"
    assert data["category"] == "Coffee"
    assert data["user_id"] == user_id
    assert "custom_mapping_id" in data

    # Verify in DB
    db_mapping = session.query(CustomMapping).filter(CustomMapping.custom_mapping_id == data["custom_mapping_id"]).first()
    assert db_mapping is not None
    assert db_mapping.merchant_keyword == "Starbucks"

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
