from typing import AsyncGenerator, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langchain_openai import ChatOpenAI
from loguru import logger

from app.config import settings


class ChatWithAI:
    def __init__(self, provider: Literal["deepseek", "chatgpt"] = "deepseek"):
        self.provider = provider
        if provider == "deepseek":
            self.llm = ChatDeepSeek(
                api_key=settings.DEEPSEEK_API_KEY,
                model=settings.DEEPSEEK_MODEL_NAME,
                temperature=0.7,
            )
        elif provider == "chatgpt":
            self.llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL_NAME,
                temperature=0.7,
            )
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {provider}")

    async def astream_response(
        self, formatted_context: str, query: str
    ) -> AsyncGenerator[str, None]:
        try:
            system_message = SystemMessage(
                content="""Ты — внутренний менеджер компании Amvera Cloud. Отвечаешь по делу без лишних вступлений. Свой ответ, в первую очередь, ориентируй на переданный контекст. Если информации недостаточно - пробуй получить ответы из своей базы знаний."""
            )
            human_message = HumanMessage(
                content=f"Вопрос: {query}\nКонтекст: {formatted_context}. Ответ форматируй в markdown!"
            )
            logger.info(f"Начинаем стриминг ответа для запроса: {query}")
            async for chunk in self.llm.astream([system_message, human_message]):
                if chunk.content:  # Пропускаем пустые куски
                    logger.debug(f"Получен чанк: {chunk.content[:50]}...")
                    yield chunk.content
            logger.info("Стриминг ответа завершен")
        except Exception as e:
            logger.error(f"Ошибка при стриминге ответа: {e}")
            yield "Произошла ошибка при стриминге ответа."
