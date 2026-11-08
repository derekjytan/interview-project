from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.context import AuthContext
from api.dependencies import DbSession
from models.conversation import Conversation, ConversationWithMessages
from service import conversation as conversation_service

router = APIRouter(prefix="/api")


class CreateConversationResponse(BaseModel):
    id: UUID


def require_conversation(
    session: Session, user_id: UUID, conversation_id: UUID
) -> Conversation:
    conversation = conversation_service.get_conversation(
        session, user_id, conversation_id
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation


@router.get("/conversations")
def list_conversations(
    session: DbSession, context: AuthContext
) -> list[ConversationWithMessages]:
    """List the caller's conversations (including archived ones) with their
    messages, most recently updated first."""
    return conversation_service.list_conversations_with_messages(
        session, context.user.id
    )


@router.get("/conversation/{conversation_id}")
def get_conversation(
    conversation_id: UUID, session: DbSession, context: AuthContext
) -> ConversationWithMessages:
    """Fetch a conversation with its messages in chronological order.

    Returns 404 when the id doesn't exist and 422 when it isn't a UUID.
    """
    conversation = require_conversation(session, context.user.id, conversation_id)
    return ConversationWithMessages(
        **conversation.model_dump(),
        messages=conversation_service.list_messages(session, conversation_id),
    )


@router.post("/conversation", status_code=201)
def create_conversation(
    session: DbSession, context: AuthContext
) -> CreateConversationResponse:
    """Create an empty conversation and return its id (201)."""
    return CreateConversationResponse(
        id=conversation_service.create_conversation(session, context.user.id)
    )


@router.post("/conversation/{conversation_id}/archive")
def archive_conversation(
    conversation_id: UUID, session: DbSession, context: AuthContext
) -> Conversation:
    """Archive a conversation (idempotent). Archived conversations are
    read-only and cannot be unarchived. Returns 404 when the id doesn't exist."""
    conversation = conversation_service.archive_conversation(
        session, context.user.id, conversation_id
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conversation
