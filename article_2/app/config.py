import os

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DEEPSEEK_API_KEY: SecretStr
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    SECRET_KEY: str
    USERS: str = os.path.join(BASE_DIR, "..", "users.json")
    ALGORITHM: str
    AMVERA_CHROMA_PATH: str = os.path.join(BASE_DIR, "chroma_db")
    AMVERA_COLLECTION_NAME: str = "amvera_docs"
    LM_MODEL_NAME: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    DEEPSEEK_MODEL_NAME: str = "deepseek-chat"
    OPENAI_MODEL_NAME: str = "gpt-3.5-turbo"
    OPENAI_API_KEY: SecretStr
    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/../.env")


settings = Config()  # type: ignore
