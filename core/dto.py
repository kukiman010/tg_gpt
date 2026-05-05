from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ChannelContext:
    user_id: int
    chat_id: int
    username: str = ""
    chat_type: str = "private"
    language_code: str = "en"


@dataclass
class InboundEvent:
    event_type: str
    context: ChannelContext
    payload: Any = None


@dataclass
class ActionCommand:
    action: str
    args: Dict[str, str]
    raw_key: str

    @property
    def is_known(self) -> bool:
        return bool(self.action)


def build_context_from_message(message) -> ChannelContext:
    username = message.chat.username or message.chat.first_name or ""
    return ChannelContext(
        user_id=message.from_user.id,
        chat_id=message.chat.id,
        username=username,
        chat_type=message.chat.type,
        language_code=message.from_user.language_code or "en",
    )

