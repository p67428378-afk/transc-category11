from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CustomMappingBase(BaseModel):
    merchant_keyword: str
    category: str

class CustomMappingCreate(CustomMappingBase):
    pass # user_id will be passed via path parameter and handled in CRUD

class CustomMappingUpdate(BaseModel):
    merchant_keyword: Optional[str] = None
    category: Optional[str] = None

class CustomMappingInDBBase(CustomMappingBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CustomMapping(CustomMappingInDBBase):
    pass
