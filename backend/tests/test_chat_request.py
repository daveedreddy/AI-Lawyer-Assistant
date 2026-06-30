import pytest
from pydantic import ValidationError

from app.api.chat import ChatRequest


def test_chat_request_rejects_blank_query():
    with pytest.raises(ValidationError):
        ChatRequest(query="   ")
