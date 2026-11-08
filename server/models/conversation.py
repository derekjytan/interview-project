from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class Role(StrEnum):
    AI = "AI"
    HUMAN = "HUMAN"


class Conversation(BaseModel):
    id: UUID
    user_id: UUID
    title: str | None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None


class ConversationMessage(BaseModel):
    id: UUID
    conversation_id: UUID
    role: Role
    content: str
    created_at: datetime


class ConversationWithMessages(Conversation):
    messages: list[ConversationMessage]
