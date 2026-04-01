import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from models import CustomMapping, Category
from schemas import CustomMappingCreate, CustomMappingUpdate
import uuid

# Assuming the router for custom mappings will be at /custom-mappings
# and the service functions will be imported into the router.

# Test for creating a custom mapping
def test_create_custom_mapping(client: TestClient, session: Session, test_data):
    category_food_id = test_data["category_food"].category_id
    user_id = str(uuid.uuid4())
    mapping_data = {
        "user_id": user_id,
        "merchant_keyword": "Local Cafe",
        "category_id": category_food_id
    }
    response = client.post("/custom-mappings/", json=mapping_data)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["merchant_keyword"] == "Local Cafe"
    assert data["category_id"] == category_food_id
    assert "mapping_id" in data

    # Verify in database
    db_mapping = session.query(CustomMapping).filter(CustomMapping.mapping_id == data["mapping_id"]).first()
    assert db_mapping is not None
    assert db_mapping.merchant_keyword == "Local Cafe"

# Test for reading custom mappings for a user
def test_read_custom_mappings_for_user(client: TestClient, session: Session, test_data):
    category_food_id = test_data["category_food"].category_id
    category_entertainment_id = test_data["category_entertainment"].category_id
    user_id = str(uuid.uuid4())

    # Add a few custom mappings for the user
    mapping1 = CustomMapping(mapping_id=str(uuid.uuid4()), user_id=user_id, merchant_keyword="User Store 1", category_id=category_food_id)
    mapping2 = CustomMapping(mapping_id=str(uuid.uuid4()), user_id=user_id, merchant_keyword="User Store 2", category_id=category_entertainment_id)
    session.add_all([mapping1, mapping2])
    session.commit()
    session.refresh(mapping1)
    session.refresh(mapping2)

    response = client.get(f"/custom-mappings/?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(m["merchant_keyword"] == "User Store 1" for m in data)
    assert any(m["merchant_keyword"] == "User Store 2" for m in data)

# Test for reading a single custom mapping by ID
def test_read_single_custom_mapping(client: TestClient, session: Session, test_data):
    category_food_id = test_data["category_food"].category_id
    user_id = str(uuid.uuid4())
    mapping = CustomMapping(mapping_id=str(uuid.uuid4()), user_id=user_id, merchant_keyword="Single Store", category_id=category_food_id)
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    response = client.get(f"/custom-mappings/{mapping.mapping_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["mapping_id"] == mapping.mapping_id
    assert data["merchant_keyword"] == "Single Store"

# Test for updating a custom mapping
def test_update_custom_mapping(client: TestClient, session: Session, test_data):
    category_food_id = test_data["category_food"].category_id
    category_utilities_id = test_data["category_utilities"].category_id
    user_id = str(uuid.uuid4())
    mapping = CustomMapping(mapping_id=str(uuid.uuid4()), user_id=user_id, merchant_keyword="Old Keyword", category_id=category_food_id)
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    update_data = {"merchant_keyword": "New Keyword", "category_id": category_utilities_id}
    response = client.put(f"/custom-mappings/{mapping.mapping_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["merchant_keyword"] == "New Keyword"
    assert data["category_id"] == category_utilities_id

    # Verify in database
    db_mapping = session.query(CustomMapping).filter(CustomMapping.mapping_id == mapping.mapping_id).first()
    assert db_mapping.merchant_keyword == "New Keyword"
    assert db_mapping.category_id == category_utilities_id

# Test for deleting a custom mapping
def test_delete_custom_mapping(client: TestClient, session: Session, test_data):
    category_food_id = test_data["category_food"].category_id
    user_id = str(uuid.uuid4())
    mapping = CustomMapping(mapping_id=str(uuid.uuid4()), user_id=user_id, merchant_keyword="To Be Deleted", category_id=category_food_id)
    session.add(mapping)
    session.commit()
    session.refresh(mapping)

    response = client.delete(f"/custom-mappings/{mapping.mapping_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Custom mapping deleted successfully"

    # Verify in database
    db_mapping = session.query(CustomMapping).filter(CustomMapping.mapping_id == mapping.mapping_id).first()
    assert db_mapping is None

# Test for custom mapping not found (read)
def test_read_custom_mapping_not_found(client: TestClient):
    response = client.get(f"/custom-mappings/{str(uuid.uuid4())}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Custom mapping not found"}

# Test for custom mapping not found (update)
def test_update_custom_mapping_not_found(client: TestClient, test_data):
    category_food_id = test_data["category_food"].category_id
    update_data = {"merchant_keyword": "NonExistent", "category_id": category_food_id}
    response = client.put(f"/custom-mappings/{str(uuid.uuid4())}", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Custom mapping not found"}

# Test for custom mapping not found (delete)
def test_delete_custom_mapping_not_found(client: TestClient):
    response = client.delete(f"/custom-mappings/{str(uuid.uuid4())}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Custom mapping not found"}

# Test for creating a duplicate custom mapping for the same user and merchant keyword
def test_create_duplicate_custom_mapping(client: TestClient, session: Session, test_data):
    category_food_id = test_data["category_food"].category_id
    user_id = str(uuid.uuid4())
    merchant_keyword = "Duplicate Merchant"
    mapping_data = {
        "user_id": user_id,
        "merchant_keyword": merchant_keyword,
        "category_id": category_food_id
    }
    response1 = client.post("/custom-mappings/", json=mapping_data)
    assert response1.status_code == 200

    response2 = client.post("/custom-mappings/", json=mapping_data)
    assert response2.status_code == 400
    assert response2.json() == {"detail": "Custom mapping with this user_id and merchant_keyword already exists"}
