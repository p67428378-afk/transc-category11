from sqlalchemy.orm import Session
from app.models.custom_mapping import CustomMapping
from app.schemas.custom_mapping import CustomMappingCreate, CustomMappingUpdate

def get_custom_mapping(db: Session, mapping_id: int):
    return db.query(CustomMapping).filter(CustomMapping.id == mapping_id).first()

def get_custom_mappings_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(CustomMapping).filter(CustomMapping.user_id == user_id).offset(skip).limit(limit).all()

def create_custom_mapping(db: Session, mapping: CustomMappingCreate, user_id: int):
    db_mapping = CustomMapping(**mapping.model_dump(), user_id=user_id)
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

def update_custom_mapping(db: Session, mapping_id: int, mapping: CustomMappingUpdate):
    db_mapping = db.query(CustomMapping).filter(CustomMapping.id == mapping_id).first()
    if db_mapping:
        update_data = mapping.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_mapping, key, value)
        db.commit()
        db.refresh(db_mapping)
    return db_mapping

def delete_custom_mapping(db: Session, mapping_id: int):
    db_mapping = db.query(CustomMapping).filter(CustomMapping.id == mapping_id).first()
    if db_mapping:
        db.delete(db_mapping)
        db.commit()
    return db_mapping
