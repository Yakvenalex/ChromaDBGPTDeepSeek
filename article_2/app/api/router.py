from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse

from app.api.schemas import AskResponse, AskWithAIResponse, SUserAuth
from app.api.utils import authenticate_user, create_jwt_token, get_current_user
from app.chroma_client.ai_store import ChatWithAI
from app.chroma_client.chroma_store import ChromaVectorStore, get_vectorstore

router = APIRouter()


@router.post("/ask")
async def ask(
    query: AskResponse,
    vectorstore: ChromaVectorStore = Depends(get_vectorstore),
    user_id: int = Depends(get_current_user),
):
    results = await vectorstore.asimilarity_search(
        query=query.response, with_score=True, k=5
    )
    formatted_results = []
    for doc, score in results:
        formatted_results.append(
            {
                "text": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": score,
            }
        )
    return {"results": formatted_results}


@router.post("/ask_with_ai")
async def ask_with_ai(
    query: AskWithAIResponse,
    vectorstore: ChromaVectorStore = Depends(get_vectorstore),
    user_id: int = Depends(get_current_user),
):
    results = await vectorstore.asimilarity_search(
        query=query.response, with_score=True, k=5
    )
    if results:
        ai_context = "\n".join([doc.page_content for doc, _ in results])
        ai_store = ChatWithAI(provider=query.provider)

        async def stream_response():
            async for chunk in ai_store.astream_response(ai_context, query.response):
                yield chunk

        return StreamingResponse(
            stream_response(),
            media_type="text/plain",
            headers={
                "Content-Type": "text/plain",
                "Transfer-Encoding": "chunked",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )
    else:
        return {"response": "Ничего не найдено"}


@router.post("/login")
async def login(
    response: Response,
    user_data: SUserAuth,
):
    user = await authenticate_user(user_data.login, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = await create_jwt_token(user["user_id"])
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Включи True в проде (HTTPS)
        samesite="lax",
        max_age=3600,
        path="/",
    )
    return {"message": "Logged in"}


@router.post("/logout")
async def logout(response: Response, user_id: int = Depends(get_current_user)):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}


@router.get("/protected")
async def protected_route(user_id: int = Depends(get_current_user)):
    return {"message": f"Hello, user {user_id}!"}
