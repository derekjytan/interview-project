from collections import defaultdict
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from entities import Conversation as ConversationEntity
from entities import ConversationMessage as MessageEntity
from models.conversation import (
    Conversation,
    ConversationMessage,
    ConversationWithMessages,
    Role,
)


def list_conversations(session: Session, user_id: UUID) -> list[Conversation]:
    """Return the user's conversations, most recently updated first."""
    rows = session.scalars(
        select(ConversationEntity)
        .where(ConversationEntity.user_id == user_id)
        .order_by(ConversationEntity.updated_at.desc())
    )
    return [Conversation.model_validate(row, from_attributes=True) for row in rows]


def list_conversations_with_messages(
    session: Session, user_id: UUID
) -> list[ConversationWithMessages]:
    """Return the user's conversations with messages in chronological order."""
    # Messages first: a conversation created in between just shows up empty.
    rows = session.scalars(
        select(MessageEntity)
        .join(
            ConversationEntity, ConversationEntity.id == MessageEntity.conversation_id
        )
        .where(ConversationEntity.user_id == user_id)
        .order_by(MessageEntity.conversation_id, MessageEntity.created_at)
    )
    messages: dict[UUID, list[ConversationMessage]] = defaultdict(list)
    for row in rows:
        messages[row.conversation_id].append(
            ConversationMessage.model_validate(row, from_attributes=True)
        )
    return [
        ConversationWithMessages(
            **conversation.model_dump(), messages=messages[conversation.id]
        )
        for conversation in list_conversations(session, user_id)
    ]


def get_conversation(
    session: Session, user_id: UUID, conversation_id: UUID
) -> Conversation | None:
    """Return the conversation only if it belongs to the given user."""
    row = session.scalar(
        select(ConversationEntity).where(
            ConversationEntity.id == conversation_id,
            ConversationEntity.user_id == user_id,
        )
    )
    return Conversation.model_validate(row, from_attributes=True) if row else None


def create_conversation(session: Session, user_id: UUID) -> UUID:
    """Insert an empty conversation for the user and return its id."""
    conversation = ConversationEntity(user_id=user_id)
    session.add(conversation)
    session.commit()
    return conversation.id


def archive_conversation(
    session: Session, user_id: UUID, conversation_id: UUID
) -> Conversation | None:
    """Archive a conversation owned by the user, preserving its first archive time."""
    row = session.scalar(
        update(ConversationEntity)
        .where(
            ConversationEntity.id == conversation_id,
            ConversationEntity.user_id == user_id,
        )
        .values(archived_at=func.coalesce(ConversationEntity.archived_at, func.now()))
        .returning(ConversationEntity)
        .execution_options(populate_existing=True)
    )
    result = Conversation.model_validate(row, from_attributes=True) if row else None
    session.commit()
    return result


def list_messages(session: Session, conversation_id: UUID) -> list[ConversationMessage]:
    """Return a conversation's messages in chronological order."""
    rows = session.scalars(
        select(MessageEntity)
        .where(MessageEntity.conversation_id == conversation_id)
        .order_by(MessageEntity.created_at)
    )
    return [
        ConversationMessage.model_validate(row, from_attributes=True) for row in rows
    ]


def record_exchange(
    session: Session,
    conversation_id: UUID,
    human_content: str,
    ai_content: str,
) -> list[ConversationMessage]:
    """Atomically save both messages, bump updated_at, and set the initial title."""
    messages = []
    for role, content in ((Role.HUMAN, human_content), (Role.AI, ai_content)):
        row = MessageEntity(
            conversation_id=conversation_id, role=role.value, content=content
        )
        session.add(row)
        # Separate inserts preserve HUMAN-before-AI clock_timestamp() ordering.
        session.flush()
        messages.append(ConversationMessage.model_validate(row, from_attributes=True))
    session.execute(
        update(ConversationEntity)
        .where(ConversationEntity.id == conversation_id)
        .values(
            updated_at=func.now(),
            title=func.coalesce(ConversationEntity.title, func.left(human_content, 80)),
        )
    )
    session.commit()
    return messages
