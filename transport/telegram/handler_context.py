from dataclasses import dataclass
from typing import Any, Callable

from Control.user import User
from core.services.assistant_service import AssistantService
from core.services.user_service import UserService
from transport.telegram.telegram_output import TelegramMessageOutput


@dataclass
class TelegramAppContext:
    bot: Any
    output: TelegramMessageOutput
    db: Any
    locale: Any
    env: Any
    speak: Any
    media_worker: Any
    pay_man: Any
    assistent_api: Any
    languages_api: Any
    tariffs_api: Any
    user_service: UserService
    assistant_service: AssistantService
    verify_callback_user: Callable[..., User]
    command_help: Callable[[User], str]
    main_menu: Callable[..., None]
    premium_button: Callable[..., None]
    pay_button: Callable[..., None]
    generate_photo: Callable[..., None]
