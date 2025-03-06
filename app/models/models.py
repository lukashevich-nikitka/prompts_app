from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class TimestampedModelMixin:
    """Mixin to add created and updated timestamps to a model."""

    @declared_attr
    def created_at(cls) -> Mapped[DateTime]:
        return mapped_column(DateTime, default=func.now())

    @declared_attr
    def updated_at(cls) -> Mapped[DateTime]:
        return mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Prompt(Base, TimestampedModelMixin):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    versions: Mapped[list["PromptVersion"]] = relationship(
        "PromptVersion", back_populates="prompt"
    )


class PromptVersion(Base, TimestampedModelMixin):
    __tablename__ = "prompt_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    commit_message: Mapped[Optional[str]] = mapped_column(String(255))

    prompt_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("prompts.id"), nullable=False
    )

    prompt: Mapped["Prompt"] = relationship("Prompt", back_populates="versions")
