# api/app/schemas/project_schema.py
from pydantic import BaseModel
from typing import List, Optional

class ProjectCreate(BaseModel):
    name: str
    description: str
    type: str

class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    type: str
    contributors: List[dict]  # Liste des contributeurs avec user_id et username

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None