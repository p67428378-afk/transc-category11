
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

# Base Schemas
class CategoryBase(BaseModel):
    category_name: str
    description: Optional[str] = None

class CategorizationRuleBase(BaseModel):
    merchant_pattern: str
    category_id: str
    priority: int = 0

class TransactionBase(BaseModel):
    external_id: str
    merchant_name: str
    amount: float
    date: datetime
    description: Optional[str] = None

class ReportedIssueBase(BaseModel):
    reported_by_user_id: str
    issue_description: Optional[str] = None
    status: str = "Open"

# Create Schemas (for POST requests)
class CategoryCreate(CategoryBase):
    pass

class CategorizationRuleCreate(CategorizationRuleBase):
    pass

class TransactionCreate(TransactionBase):
    assigned_category_id: Optional[str] = None

class ReportedIssueCreate(ReportedIssueBase):
    pass

# Response Schemas (for GET/POST responses)
class CategoryResponse(CategoryBase):
    category_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CategorizationRuleResponse(CategorizationRuleBase):
    rule_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    category: CategoryResponse # Nested category response

    class Config:
        from_attributes = True

class TransactionResponse(TransactionBase):
    transaction_id: str
    assigned_category_id: Optional[str] = None
    manual_override: bool
    flagged_for_review: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_category: Optional[CategoryResponse] = None # Nested category response

    class Config:
        from_attributes = True

class ReportedIssueResponse(ReportedIssueBase):
    issue_id: str
    transaction_id: str # Add transaction_id back for the response model
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Update Schemas
class TransactionUpdateCategory(BaseModel):
    assigned_category_id: str
