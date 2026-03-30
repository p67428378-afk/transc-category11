import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.custom_mapping import CustomMapping
from app.schemas.custom_mapping import CustomMappingCreate, CustomMappingUpdate

# Assuming app.main.app is your FastAPI application instance
client = TestClient(app)

def test_create_custom_mapping(session: Session):
    user_id = 1
    mapping_data = {"merchant_keyword": "TestMerchant", "category": "TestCategory"}
    response = client.post(f"/api/v1/users/{user_id}/mappings/", json=mapping_data)
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_keyword"] == "TestMerchant"
    assert data["category"] == "TestCategory"
    assert data["user_id"] == user_id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    db_mapping = session.query(CustomMapping).filter(CustomMapping.id == data["id"]).first()
    assert db_mapping is not None
    assert db_mapping.merchant_keyword == "TestMerchant"

def test_get_custom_mappings_by_user(session: Session):
    user_id = 1
    mapping1 = CustomMapping(user_id=user_id, merchant_keyword="Merchant1", category="Category1")
    mapping2 = CustomMapping(user_id=user_id, merchant_keyword="Merchant2", category="Category2")
    session.add_all([mapping1, mapping2])
    session.commit()
    session.refresh(mapping1)
    session.refresh(mapping2)

    response = client.get(f"/api/v1/users/{user_id}/mappings/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["merchant_keyword"] == "Merchant1"
    assert data[1]["merchant_keyword"] == "Merchant2"

def test_get_custom_mapping(session: Session):
    user_id = 1
    mapping = CustomMapping(user_id=user_id, merchant_keyword="SingleMerchant", category="SingleCategory")
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    response = client.get(f"/api/v1/users/{user_id}/mappings/{mapping.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_keyword"] == "SingleMerchant"
    assert data["category"] == "SingleCategory"
    assert data["id"] == mapping.id

def test_update_custom_mapping_partial(session: Session):
    user_id = 1
    mapping = CustomMapping(user_id=user_id, merchant_keyword="OldMerchant", category="OldCategory")
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    update_data = {"merchant_keyword": "NewMerchant"}
    response = client.patch(f"/api/v1/users/{user_id}/mappings/{mapping.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_keyword"] == "NewMerchant"
    assert data["category"] == "OldCategory"  # Should remain unchanged
    assert data["id"] == mapping.id

    db_mapping = session.query(CustomMapping).filter(CustomMapping.id == mapping.id).first()
    assert db_mapping.merchant_keyword == "NewMerchant"
    assert db_mapping.category == "OldCategory"

def test_update_custom_mapping_full(session: Session):
    user_id = 1
    mapping = CustomMapping(user_id=user_id, merchant_keyword="OldMerchant2", category="OldCategory2")
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    update_data = {"merchant_keyword": "NewMerchant2", "category": "NewCategory2"}
    response = client.patch(f"/api/v1/users/{user_id}/mappings/{mapping.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_keyword"] == "NewMerchant2"
    assert data["category"] == "NewCategory2"
    assert data["id"] == mapping.id

    db_mapping = session.query(CustomMapping).filter(CustomMapping.id == mapping.id).first()
    assert db_mapping.merchant_keyword == "NewMerchant2"
    assert db_mapping.category == "NewCategory2"

def test_delete_custom_mapping(session: Session):
    user_id = 1
    mapping = CustomMapping(user_id=user_id, merchant_keyword="ToDelete", category="CategoryToDelete")
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    response = client.delete(f"/api/v1/users/{user_id}/mappings/{mapping.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Mapping deleted successfully"

    db_mapping = session.query(CustomMapping).filter(CustomMapping.id == mapping.id).first()
    assert db_mapping is None

def test_delete_non_existent_custom_mapping(session: Session):
    user_id = 1
    non_existent_id = 999
    response = client.delete(f"/api/v1/users/{user_id}/mappings/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Mapping not found"

def test_update_non_existent_custom_mapping(session: Session):
    user_id = 1
    non_existent_id = 999
    update_data = {"merchant_keyword": "NewMerchant"}
    response = client.patch(f"/api/v1/users/{user_id}/mappings/{non_existent_id}", json=update_data)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Mapping not found"
