from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from db import get_db
from service.openai import OpenAIChatService, openai_chat_service

DbSession = Annotated[Session, Depends(get_db)]


def get_chat_service() -> OpenAIChatService:
    return openai_chat_service


ChatService = Annotated[OpenAIChatService, Depends(get_chat_service)]
