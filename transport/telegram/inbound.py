"""Маппинг Telegram Message → core DTO (общий контракт с будущим VK)."""

from typing import Any, Optional

from core.dto import InboundEvent, build_context_from_message


def inbound_from_telegram_message(
    message,
    event_type: str,
    payload: Optional[Any] = None,
) -> InboundEvent:
    """Собрать InboundEvent из telebot Message (текст, команда, медиа — различаются event_type)."""
    if payload is None:
        payload = getattr(message, "text", None)
    return InboundEvent(
        event_type=event_type,
        context=build_context_from_message(message),
        payload=payload,
    )


def inbound_telegram_command(message, command: str, args_text: Optional[str] = None) -> InboundEvent:
    return InboundEvent(
        event_type="telegram_command",
        context=build_context_from_message(message),
        payload={"command": command, "args": args_text},
    )
