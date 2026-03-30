from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.custom_mapping import (create_custom_mapping, get_custom_mapping, get_custom_mappings_by_user, update_custom_mapping, delete_custom_mapping)
from app.schemas.custom_mapping import CustomMapping, CustomMappingCreate, CustomMappingUpdate
from app.database import get_db

router = APIRouter()

# Dependency to get the current user ID (mocked for now)
def get_current_user_id():
    # In a real application, this would extract user ID from a JWT token
    return 1  # Mock user ID for testing

@router.post("/users/{user_id}/mappings/", response_model=CustomMapping, status_code=status.HTTP_200_OK)
def create_custom_mapping_api(
    user_id: int,
    mapping: CustomMappingCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create mappings for this user")
    return create_custom_mapping(db=db, mapping=mapping, user_id=user_id)

@router.get("/users/{user_id}/mappings/", response_model=List[CustomMapping])
def read_custom_mappings_api(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    if user_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view mappings for this user")
    mappings = get_custom_mappings_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    return mappings

@router.get("/users/{user_id}/mappings/{mapping_id}", response_model=CustomMapping)
def read_custom_mapping_api(
    user_id: int,
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    if db_mapping := get_custom_mapping(db=db, mapping_id=mapping_id):
        if user_id != current_user_id or db_mapping.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this mapping")
        return db_mapping
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")

@router.patch("/users/{user_id}/mappings/{mapping_id}", response_model=CustomMapping)
def update_custom_mapping_api(
    user_id: int,
    mapping_id: int,
    mapping: CustomMappingUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    if db_mapping := get_custom_mapping(db=db, mapping_id=mapping_id):
        if user_id != current_user_id or db_mapping.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this mapping")
        return update_custom_mapping(db=db, mapping_id=mapping_id, mapping=mapping)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")

@router.delete("/users/{user_id}/mappings/{mapping_id}", status_code=status.HTTP_200_OK)
def delete_custom_mapping_api(
    user_id: int,
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    if db_mapping := get_custom_mapping(db=db, mapping_id=mapping_id):
        if user_id != current_user_id or db_mapping.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this mapping")
        delete_custom_mapping(db=db, mapping_id=mapping_id)
        return {"message": "Mapping deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")
