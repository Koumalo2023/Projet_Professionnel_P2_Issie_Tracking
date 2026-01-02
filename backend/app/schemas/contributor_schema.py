# api/app/schemas/contributor_schema.py
from pydantic import BaseModel

class ContributorCreate(BaseModel):
    user_id: int

class ContributorResponse(BaseModel):
    user_id: int
    username: str