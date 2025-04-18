from fastapi import APIRouter, Depends
from app.chroma_client.chroma_store import ChromaVectorStore, get_vectorstore


router = APIRouter()


@router.get("/ask")
async def ask(query: str, vectorstore: ChromaVectorStore = Depends(get_vectorstore)):
    results = await vectorstore.asimilarity_search(query=query, with_score=True)
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
