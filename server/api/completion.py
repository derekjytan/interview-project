from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.context import AuthContext
from api.conversation import require_conversation
from api.dependencies import ChatService, DbSession
from models.chat import ChatModel
from models.conversation import ConversationMessage, Role
from service import conversation as conversation_service
from service.openai import ChatTurn, ModelServiceError

router = APIRouter(prefix="/api")


class CompletionRequest(BaseModel):
    content: str = Field(min_length=1)
    model: ChatModel


@router.post("/chat/completion/{conversation_id}")
def chat_completion(
    conversation_id: UUID,
    request: CompletionRequest,
    session: DbSession,
    service: ChatService,
    context: AuthContext,
) -> list[ConversationMessage]:
    """Send a message and return the saved [HUMAN, AI] pair.

    Prior history is loaded from the database; nothing is persisted when the
    model call fails. Returns 404 for an unknown conversation, 422 for an
    invalid UUID or body, 409 for an archived conversation, and the
    ModelServiceError-mapped statuses (429, 502, 503, 504) when the model
    call fails.
    """
    conversation = require_conversation(session, context.user.id, conversation_id)
    if conversation.archived_at is not None:
        raise HTTPException(status_code=409, detail="This conversation is archived.")
    history = conversation_service.list_messages(session, conversation_id)
    turns = [
        *(ChatTurn(m.role, m.content) for m in history),
        ChatTurn(Role.HUMAN, request.content),
    ]
    # All history is now detached Pydantic data. Release the read transaction
    # and pooled connection before waiting for the external model service.
    session.rollback()
    try:
        completion = service.complete(turns, request.model)
    except ModelServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc
    return conversation_service.record_exchange(
        session, conversation_id, request.content, completion.content
    )
