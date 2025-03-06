from typing import Optional

from pydantic import BaseModel


class CreatePromptInDTO(BaseModel):
    title: str
    description: str
    content: str
    commit_message: Optional[str]


class UpdatePromptInDTO(BaseModel):
    content: str
    commit_message: Optional[str]
