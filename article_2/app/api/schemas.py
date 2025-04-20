from typing import Literal

from pydantic import BaseModel


class AskResponse(BaseModel):
    response: str


class AskWithAIResponse(BaseModel):
    response: str
    provider: Literal["deepseek", "chatgpt"] = "deepseek"


class SUserAuth(BaseModel):
    login: str
    password: str
