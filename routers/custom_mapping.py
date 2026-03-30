from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import CustomMapping
from schemas import CustomMappingCreate, CustomMappingResponse, CustomMappingUpdate

router = APIRouter()

# Dependency to get the current user ID (mock for now)
def get_current_user_id():
    # In a real application, this would extract user ID from a JWT token
    # For now, we'll use a placeholder or extract from path for testing purposes
    return "test_user_id" # Placeholder

@router.post("/user/{user_id}/mappings", response_model=CustomMappingResponse, status_code=status.HTTP_200_OK)
def create_custom_mapping(
    user_id: str,
    mapping: CustomMappingCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id) # Placeholder for auth
):
    # In a real app, ensure current_user_id matches user_id from path or is authorized
    # For now, we'll allow creation for any user_id in the path

    db_mapping = CustomMapping(
        user_id=user_id,
        merchant_keyword=mapping.merchant_keyword,
        category=mapping.category
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/user/{user_id}/mappings", response_model=List[CustomMappingResponse])
def get_custom_mappings_for_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id) # Placeholder for auth
):
    # In a real app, ensure current_user_id matches user_id from path or is authorized
    mappings = db.query(CustomMapping).filter(CustomMapping.user_id == user_id).all()
    return mappings

@router.get("/user/{user_id}/mappings/{mapping_id}", response_model=CustomMappingResponse)
def get_single_custom_mapping(
    user_id: str,
    mapping_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id) # Placeholder for auth
):
    # In a real app, ensure current_user_id matches user_id from path or is authorized
    mapping = db.query(CustomMapping).filter(
        CustomMapping.user_id == user_id,
        CustomMapping.custom_mapping_id == mapping_id
    ).first()
    if not mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom mapping not found")
    return mapping

@router.put("/user/{user_id}/mappings/{mapping_id}", response_model=CustomMappingResponse)
def update_custom_mapping(
    user_id: str,
    mapping_id: str,
    mapping_update: CustomMappingUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id) # Placeholder for auth
):
    # In a real app, ensure current_user_id matches user_id from path or is authorized
    db_mapping = db.query(CustomMapping).filter(
        CustomMapping.user_id == user_id,
        CustomMapping.custom_mapping_id == mapping_id
    ).first()
    if not db_mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom mapping not found")

    update_data = mapping_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_mapping, key, value)

    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.delete("/user/{user_id}/mappings/{mapping_id}", status_code=status.HTTP_200_OK)
def delete_custom_mapping(
    user_id: str,
    mapping_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id) # Placeholder for auth
):
    # In a real app, ensure current_user_id matches user_id from path or is authorized
    db_mapping = db.query(CustomMapping).filter(
        CustomMapping.user_id == user_id,
        CustomMapping.custom_mapping_id == mapping_id
    ).first()
    if not db_mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom mapping not found")

    db.delete(db_mapping)
    db.commit()
    return {"message": "Custom mapping deleted successfully"}
