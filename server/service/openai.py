import os
from dataclasses import dataclass
from functools import cache
from typing import Literal, assert_never

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)

from models.chat import ChatModel
from models.conversation import Role


@dataclass(frozen=True)
class ChatTurn:
    role: Role
    content: str


def to_openai_role(role: Role) -> Literal["user", "assistant"]:
    """Map a conversation Role onto the OpenAI input role names."""
    match role:
        case Role.HUMAN:
            return "user"
        case Role.AI:
            return "assistant"
        case _:
            assert_never(role)


@dataclass(frozen=True)
class CompletionResult:
    id: str
    created: int
    model: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ModelServiceError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


@cache
def get_openai_client() -> OpenAI:
    """Build the shared OpenAI client.

    Cached for the process lifetime. Raises ModelServiceError(503) when
    OPENAI_API_KEY is unset; OPENAI_BASE_URL is optional.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ModelServiceError(
            status_code=503,
            detail=(
                "The AI service is not configured. "
                "Set OPENAI_API_KEY in .env at the project root."
            ),
        )
    return OpenAI(
        api_key=api_key,
        # Compose passes "" when unset; None lets the SDK use api.openai.com.
        base_url=os.getenv("OPENAI_BASE_URL") or None,
        timeout=30.0,
        max_retries=2,
    )


class OpenAIChatService:
    def complete(
        self, turns: list[ChatTurn], model: ChatModel
    ) -> CompletionResult:
        """Send the turns to the model and return its reply with usage stats.

        OpenAI SDK errors are mapped to ModelServiceError with HTTP-style
        status codes: 429 rate limit, 504 timeout, 503 auth/config, 502 for
        other API failures or an empty response.
        """
        input_messages = [
            {"role": to_openai_role(turn.role), "content": turn.content}
            for turn in turns
        ]

        try:
            response = get_openai_client().responses.create(
                model=model.value,
                input=input_messages,
            )
        except ModelServiceError:
            raise
        except RateLimitError as exc:
            raise ModelServiceError(
                status_code=429,
                detail="The AI service is busy. Please try again shortly.",
            ) from exc
        except APITimeoutError as exc:
            raise ModelServiceError(
                status_code=504,
                detail="The AI service took too long to respond.",
            ) from exc
        except (AuthenticationError, PermissionDeniedError) as exc:
            raise ModelServiceError(
                status_code=503,
                detail="The AI service is not configured correctly.",
            ) from exc
        except (APIConnectionError, APIStatusError) as exc:
            raise ModelServiceError(
                status_code=502,
                detail="The AI service is temporarily unavailable.",
            ) from exc

        if not response.output_text:
            raise ModelServiceError(
                status_code=502,
                detail="The AI service returned an empty response.",
            )

        usage = response.usage
        prompt_tokens = usage.input_tokens if usage else 0
        completion_tokens = usage.output_tokens if usage else 0
        total_tokens = usage.total_tokens if usage else 0

        return CompletionResult(
            id=response.id,
            created=int(response.created_at),
            model=response.model,
            content=response.output_text,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )


openai_chat_service = OpenAIChatService()
