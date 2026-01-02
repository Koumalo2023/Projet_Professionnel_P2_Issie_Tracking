# api/app/schemas/issue_schema.py
from pydantic import BaseModel
from typing import Optional

class IssueCreate(BaseModel):
    name: str
    description: str
    priority: str
    tag: str
    assigned_to: int

class IssueResponse(BaseModel):
    id: int
    name: str
    description: str
    priority: str
    tag: str
    status: str
    assigned_to: int

class IssueUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    tag: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[int] = None