from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from schemas import CustomMappingCreate, CustomMappingUpdate, CustomMappingResponse
from services import mapping_service
from database import get_db

router = APIRouter(
    prefix="/custom-mappings",
    tags=["Custom Mappings"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/",
    response_model=CustomMappingResponse,
    status_code=status.HTTP_200_OK,
    summary="Create a new custom merchant-to-category mapping",
    description="Allows users to define a new custom rule for categorizing transactions."
)
def create_custom_mapping(mapping: CustomMappingCreate, db: Session = Depends(get_db)):
    return mapping_service.create_custom_mapping(db=db, mapping=mapping)

@router.get(
    "/",
    response_model=List[CustomMappingResponse],
    summary="Retrieve all custom mappings for a specific user",
    description="Fetches a list of all custom merchant-to-category mappings defined by a user."
)
def read_custom_mappings_for_user(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    mappings = mapping_service.get_custom_mappings_by_user(db=db, user_id=user_id, skip=skip, limit=limit)
    return mappings

@router.get(
    "/{mapping_id}",
    response_model=CustomMappingResponse,
    summary="Retrieve a single custom mapping by ID",
    description="Fetches details of a specific custom merchant-to-category mapping using its ID."
)
def read_custom_mapping(mapping_id: str, db: Session = Depends(get_db)):
    db_mapping = mapping_service.get_custom_mapping(db=db, mapping_id=mapping_id)
    if db_mapping is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom mapping not found")
    return db_mapping

@router.put(
    "/{mapping_id}",
    response_model=CustomMappingResponse,
    summary="Update an existing custom mapping",
    description="Modifies an existing custom merchant-to-category mapping identified by its ID."
)
def update_custom_mapping(mapping_id: str, mapping: CustomMappingUpdate, db: Session = Depends(get_db)):
    return mapping_service.update_custom_mapping(db=db, mapping_id=mapping_id, mapping_update=mapping)

@router.delete(
    "/{mapping_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a custom mapping",
    description="Removes a custom merchant-to-category mapping identified by its ID."
)
def delete_custom_mapping(mapping_id: str, db: Session = Depends(get_db)):
    return mapping_service.delete_custom_mapping(db=db, mapping_id=mapping_id)
