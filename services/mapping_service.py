from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import CustomMapping, Category
from schemas import CustomMappingCreate, CustomMappingUpdate
from fastapi import HTTPException, status
import uuid

def get_custom_mapping(db: Session, mapping_id: str):
    return db.query(CustomMapping).filter(CustomMapping.mapping_id == mapping_id).first()

def get_custom_mappings_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100):
    return db.query(CustomMapping).filter(CustomMapping.user_id == user_id).offset(skip).limit(limit).all()

def create_custom_mapping(db: Session, mapping: CustomMappingCreate):
    # Check if category_id exists
    category = db.query(Category).filter(Category.category_id == mapping.category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Check for existing mapping for the same user and merchant_keyword
    existing_mapping = db.query(CustomMapping).filter(
        CustomMapping.user_id == mapping.user_id,
        CustomMapping.merchant_keyword == mapping.merchant_keyword
    ).first()
    if existing_mapping:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Custom mapping with this user_id and merchant_keyword already exists")

    db_mapping = CustomMapping(
        mapping_id=str(uuid.uuid4()),
        user_id=mapping.user_id,
        merchant_keyword=mapping.merchant_keyword,
        category_id=mapping.category_id
    )
    try:
        db.add(db_mapping)
        db.commit()
        db.refresh(db_mapping)
        return db_mapping
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create custom mapping due to data integrity issue.")

def update_custom_mapping(db: Session, mapping_id: str, mapping_update: CustomMappingUpdate):
    db_mapping = get_custom_mapping(db, mapping_id)
    if not db_mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom mapping not found")

    if mapping_update.category_id:
        category = db.query(Category).filter(Category.category_id == mapping_update.category_id).first()
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    update_data = mapping_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_mapping, key, value)

    try:
        db.add(db_mapping)
        db.commit()
        db.refresh(db_mapping)
        return db_mapping
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not update custom mapping due to data integrity issue.")

def delete_custom_mapping(db: Session, mapping_id: str):
    db_mapping = get_custom_mapping(db, mapping_id)
    if not db_mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Custom mapping not found")

    db.delete(db_mapping)
    db.commit()
    return {"message": "Custom mapping deleted successfully"}
