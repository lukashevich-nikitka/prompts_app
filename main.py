"""
Sets up a FastAPI app with custom lifespan management, logging, and a health check endpoint.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.db.session import sessionmanager
from app.routers.prompts_router import PromptsRouter


@asynccontextmanager
async def lifespan(_: FastAPI):

    yield

    if sessionmanager.engine is not None:
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan, title="Prompts_app", docs_url="/api/docs")
app.include_router(PromptsRouter)


@app.get("/health-check", status_code=200)
async def root():
    """
    Simple health check endpoint.
    """
    return {"message": "OK"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
