"""Schemas for the prompts sqlalchemy orm models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PromptDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    versions: list
    created_at: datetime
    updated_at: datetime


class PromptVersionDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    version: int
    content: str
    commit_message: Optional[str]
    prompt_id: int
    created_at: datetime
    updated_at: datetime
