from langchain_huggingface import HuggingFaceEmbeddings
import torch
from loguru import logger
from langchain_chroma import Chroma

CHROMA_PATH = r"C:\Users\mrmno\CursorPythonProjects\chroma_project\article_1\examples\shop_chroma_db"
COLLECTION_NAME = "shop_data"


def connect_to_chroma():
    """Подключение к существующей базе Chroma."""
    try:
        logger.info("Загрузка модели эмбеддингов...")
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        chroma_db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name=COLLECTION_NAME,
        )

        logger.success("Успешное подключение к базе Chroma")
        return chroma_db
    except Exception as e:
        logger.error(f"Ошибка подключения к Chroma: {e}")
        raise


def search_products(query: str, metadata_filter: dict = None, k: int = 4):
    """
    Поиск продуктов по запросу и метаданным.

    Args:
        query (str): Текстовый запрос для поиска
        metadata_filter (dict): Опциональный фильтр по метаданным
        k (int): Количество результатов для возврата

    Returns:
        list: Список найденных продуктов с их метаданными
    """
    try:
        chroma_db = connect_to_chroma()
        results = chroma_db.similarity_search_with_score(
            query, k=k, filter=metadata_filter
        )

        logger.info(f"Найдено {len(results)} результатов для запроса: {query}")
        formatted_results = []
        for doc, score in results:
            formatted_results.append(
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score,
                }
            )
        return formatted_results
    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        raise


for i in search_products(query="какой у вас самый крутой пылесос?"):
    print(i)
