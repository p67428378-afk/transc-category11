from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/api/v1/users/{user_id}/mappings",
    tags=["Custom Mappings"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.CustomMappingInDB, status_code=status.HTTP_201_CREATED)
def create_custom_mapping(
    user_id: str,
    mapping: schemas.CustomMappingCreate,
    db: Session = Depends(get_db)
):
    db_mapping = db.query(models.CustomMapping).filter(
        models.CustomMapping.user_id == user_id,
        models.CustomMapping.merchant_keyword == mapping.merchant_keyword
    ).first()
    if db_mapping:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Custom mapping for this merchant keyword already exists for this user")

    db_mapping = models.CustomMapping(**mapping.model_dump(), user_id=user_id)
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.get("/", response_model=List[schemas.CustomMappingInDB])
def get_custom_mappings(
    user_id: str,
    db: Session = Depends(get_db)
):
    mappings = db.query(models.CustomMapping).filter(models.CustomMapping.user_id == user_id).all()
    return mappings

@router.get("/{mapping_id}", response_model=schemas.CustomMappingInDB)
def get_custom_mapping_by_id(
    user_id: str,
    mapping_id: int,
    db: Session = Depends(get_db)
):
    db_mapping = db.query(models.CustomMapping).filter(
        models.CustomMapping.id == mapping_id,
        models.CustomMapping.user_id == user_id
    ).first()
    if db_mapping is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")
    return db_mapping

@router.put("/{mapping_id}", response_model=schemas.CustomMappingInDB)
def update_custom_mapping(
    user_id: str,
    mapping_id: int,
    mapping: schemas.CustomMappingUpdate,
    db: Session = Depends(get_db)
):
    db_mapping = db.query(models.CustomMapping).filter(
        models.CustomMapping.id == mapping_id,
        models.CustomMapping.user_id == user_id
    ).first()
    if db_mapping is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")

    for key, value in mapping.model_dump(exclude_unset=True).items():
        setattr(db_mapping, key, value)

    db.commit()
    db.refresh(db_mapping)
    return db_mapping

@router.delete("/{mapping_id}", status_code=status.HTTP_200_OK)
def delete_custom_mapping(
    user_id: str,
    mapping_id: int,
    db: Session = Depends(get_db)
):
    db_mapping = db.query(models.CustomMapping).filter(
        models.CustomMapping.id == mapping_id,
        models.CustomMapping.user_id == user_id
    ).first()
    if db_mapping is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mapping not found")

    db.delete(db_mapping)
    db.commit()
    return {"message": "Mapping deleted successfully"}
