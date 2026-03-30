from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import CustomMapping
import schemas # Changed import statement

router = APIRouter()

# Dependency to get the current user ID (mock for now)
def get_current_user_id():
    # In a real application, this would extract user ID from a JWT token
    # For now, we'll use a placeholder or extract from path for testing purposes
    return "test_user_id" # Placeholder

@router.post("/user/{user_id}/mappings", response_model=schemas.CustomMappingResponse, status_code=status.HTTP_201_CREATED)
def create_custom_mapping(
    user_id: str,
    mapping: schemas.CustomMappingCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id) # Placeholder for auth
):
    # In a real app, ensure current_user_id matches user_id from path or is authorized
    # For now, we'll allow creation for any user_id in the path

    # Check for existing mapping before creation to handle uniqueness at application level
    existing_mapping = db.query(CustomMapping).filter(
        CustomMapping.user_id == user_id,
        CustomMapping.merchant_keyword == mapping.merchant_keyword
    ).first()

    if existing_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Custom mapping with this merchant keyword already exists for this user."
        )

    db_mapping = CustomMapping(
        user_id=user_id,
        merchant_keyword=mapping.merchant_keyword,
        category=mapping.category
    )
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/user/{user_id}/mappings", response_model=List[schemas.CustomMappingResponse])
def get_custom_mappings_for_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id) # Placeholder for auth
):
    # In a real app, ensure current_user_id matches user_id from path or is authorized
    mappings = db.query(CustomMapping).filter(CustomMapping.user_id == user_id).all()
    return mappings

@router.get("/user/{user_id}/mappings/{mapping_id}", response_model=schemas.CustomMappingResponse)
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

@router.put("/user/{user_id}/mappings/{mapping_id}", response_model=schemas.CustomMappingResponse)
def update_custom_mapping(
    user_id: str,
    mapping_id: str,
    mapping_update: schemas.CustomMappingUpdate,
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

    # Check for uniqueness if merchant_keyword is being updated
    if "merchant_keyword" in update_data and update_data["merchant_keyword"] != db_mapping.merchant_keyword:
        existing_mapping = db.query(CustomMapping).filter(
            CustomMapping.user_id == user_id,
            CustomMapping.merchant_keyword == update_data["merchant_keyword"],
            CustomMapping.custom_mapping_id != mapping_id # Exclude the current mapping
        ).first()
        if existing_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Update would create a duplicate custom mapping for this user and merchant keyword."
            )

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
