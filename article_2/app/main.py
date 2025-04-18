from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router as api_router
from app.chroma_client.chroma_store import chroma_vectorstore


@asynccontextmanager
async def lifespan(app: FastAPI):
    await chroma_vectorstore.init()
    app.include_router(api_router, prefix="/api", tags=["API"])
    yield
    await chroma_vectorstore.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}
