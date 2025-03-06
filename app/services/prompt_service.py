from typing import Optional

from fastapi import Depends

from app.models.models import Prompt, PromptVersion
from app.models.schemas import PromptDTO, PromptVersionDTO
from app.repository.repository import AppRepoInterface, PromptsAppRepository
from app.routers.dto import CreatePromptInDTO


class DatabaseError(Exception):
    pass


class NotFoundError(Exception):
    pass


class PromptsService:
    def __init__(self, repo: AppRepoInterface = Depends(PromptsAppRepository)) -> None:
        self.repo: AppRepoInterface = repo

    async def get_one(self, prompt_id: int, version_id: int) -> PromptVersionDTO:
        return await self.repo.get(
            PromptVersion,
            which=[
                PromptVersion.version == version_id,
                PromptVersion.prompt_id == prompt_id,
            ],
        )

    async def create_prompt(self, prompt: CreatePromptInDTO) -> PromptVersionDTO:
        base_prompt: PromptDTO = await self.repo.create(
            Prompt(
                title=prompt.title,
                description=prompt.description,
            )
        )
        if base_prompt is None:
            raise DatabaseError("Failed to create base prompt")

        init_version: int = 1
        return await self.create_prompt_version(
            base_prompt.id, prompt.content, init_version, prompt.commit_message
        )

    async def create_prompt_version(
        self,
        prompt_id: int,
        content: str,
        version: Optional[int] = None,
        commit_message: Optional[str] = None,
    ) -> PromptVersionDTO:
        return await self.repo.create(
            PromptVersion(
                version=version or await self._get_next_version(prompt_id),
                content=content,
                commit_message=commit_message,
                prompt_id=prompt_id,
            )
        )

    async def update_prompt_version(
        self,
        prompt_id: int,
        content: str,
        version: Optional[int] = None,
        commit_message: Optional[str] = None,
    ) -> PromptVersionDTO:
        if await self.repo.get(Prompt, which=[Prompt.id == prompt_id]):
            return await self.create_prompt_version(
                prompt_id, content, version, commit_message
            )
        raise NotFoundError(f"Base with id: {prompt_id} prompt do not exist")

    async def _get_next_version(self, prompt_id: int) -> int:
        latest_version: PromptVersionDTO = await self.repo.get(
            PromptVersion,
            which=[PromptVersion.prompt_id == prompt_id],
            order_by=[PromptVersion.version.desc()],
            many=False,
        )
        if latest_version:
            return latest_version.version + 1
        else:
            return 1

    async def delete_prompt_version(self, prompt_id: int, version_id: int) -> bool:
        return await self.repo.delete(
            PromptVersion,
            which=[
                PromptVersion.version == version_id,
                PromptVersion.prompt_id == prompt_id,
            ],
        )

    async def get_all_versions(self, prompt_id: int) -> list[PromptVersionDTO]:
        return await self.repo.get(
            PromptVersion,
            which=[PromptVersion.prompt_id == prompt_id],
            order_by=[PromptVersion.version.asc()],
            many=True,
        )
