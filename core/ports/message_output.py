from typing import Any, Optional, Protocol


class MessageOutputPort(Protocol):
    """Transport-agnostic outbound messages (implemented per channel)."""

    def send_text(
        self,
        chat_id: int,
        text: str,
        reply_markup: Any = None,
        id_message_for_edit: Optional[int] = None,
        isMarkdown: bool = False,
    ) -> None:
        ...

    def delete_message(self, chat_id: int, message_id: int) -> None:
        ...
