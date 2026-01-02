# api/app/schemas/comment_schema.py
from pydantic import BaseModel
from typing import Optional

class CommentCreate(BaseModel):
    description: str

class CommentResponse(BaseModel):
    id: int
    description: str
    author: int

class CommentUpdate(BaseModel):
    description: Optional[str] = None