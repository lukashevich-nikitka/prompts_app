from fastapi import APIRouter, Depends, HTTPException, status

from app.models.schemas import PromptVersionDTO
from app.routers.dto import CreatePromptInDTO, UpdatePromptInDTO
from app.services.prompt_service import NotFoundError, PromptsService

PromptsRouter = APIRouter(
    prefix="/prompts",
    tags=["propmpts"],
)


@PromptsRouter.get("version/{prompt_id}/{version_id}", status_code=status.HTTP_200_OK)
async def get_prompt_version(
    prompt_id,
    version_id,
    prompts_service: PromptsService = Depends(PromptsService),
) -> PromptVersionDTO:
    prompt_version: PromptVersionDTO = await prompts_service.get_one(
        int(prompt_id), int(version_id)
    )
    if prompt_version:
        return prompt_version
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found"
        )


@PromptsRouter.post("/create", status_code=status.HTTP_201_CREATED)
async def create_prompt_version(
    prompt: CreatePromptInDTO,
    prompts_service: PromptsService = Depends(PromptsService),
) -> PromptVersionDTO:
    prompt_version = await prompts_service.create_prompt(prompt)
    if prompt_version:
        return prompt_version
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create prompt",
        )


@PromptsRouter.put("/update/{prompt_id}/", status_code=status.HTTP_200_OK)
async def update_prompt_version(
    prompt_id,
    prompt: UpdatePromptInDTO,
    prompts_service: PromptsService = Depends(PromptsService),
) -> PromptVersionDTO:
    try:
        new_version: PromptVersionDTO = await prompts_service.update_prompt_version(
            int(prompt_id), prompt.content, commit_message=prompt.commit_message
        )
        if new_version:
            return new_version
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update prompt",
            )

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Base with id: {prompt_id} prompt do not exist",
        )


@PromptsRouter.delete(
    "/delete/prompt_version/{prompt_id}/{version_id}", status_code=status.HTTP_200_OK
)
async def delete_prompt_version(
    prompt_id,
    version_id,
    prompts_service: PromptsService = Depends(PromptsService),
) -> None:
    if not await prompts_service.delete_prompt_version(int(prompt_id), int(version_id)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete prompt version",
        )


@PromptsRouter.get("/all_versions/{prompt_id}", status_code=status.HTTP_200_OK)
async def versions(
    prompt_id,
    prompts_service: PromptsService = Depends(PromptsService),
) -> list[PromptVersionDTO]:
    return await prompts_service.get_all_versions(int(prompt_id))
