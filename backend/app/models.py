"""API request and response models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.config import RequestClass


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=16_000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: list[ChatMessage] = Field(min_length=1)
    request_class: RequestClass = RequestClass.INTERACTIVE
    max_tokens: int = Field(default=256, ge=1, le=4096)


class ChatResponse(BaseModel):
    provider: str
    request_class: RequestClass
    reply: str
    simulated: bool = True


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    providers: dict[str, Literal["healthy", "unhealthy"]]
