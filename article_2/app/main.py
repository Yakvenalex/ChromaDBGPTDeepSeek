from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import router as api_router
from app.chroma_client.chroma_store import chroma_vectorstore
from app.pages.router import router as page_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await chroma_vectorstore.init()
    app.include_router(api_router, prefix="/api", tags=["API"])
    app.include_router(page_router, tags=["ФРОНТ"])
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    yield
    await chroma_vectorstore.close()


app = FastAPI(lifespan=lifespan)
