import re
from typing import Optional

from core.dto import ActionCommand


class CallbackCodec:
    _PATTERNS = [
        ("assistant_select", re.compile(r"^set_model_(\d+)$"), ("id",)),
        ("language_select", re.compile(r"^set_lang_model_(\d+)$"), ("id",)),
        ("payment_select", re.compile(r"^set_payments_(\S+)_(\d+)$"), ("system", "tariff_id")),
        ("tariff_select", re.compile(r"^set_tariff_model_(\d+)$"), ("id",)),
        ("check_payment", re.compile(r"^check_pay_(\S+-\S+-\S+-\S+)$"), ("payment_id",)),
    ]

    @staticmethod
    def encode_assistant_select(idx: int) -> str:
        return f"set_model_{idx}"

    @staticmethod
    def encode_language_select(idx: int) -> str:
        return f"set_lang_model_{idx}"

    @staticmethod
    def encode_tariff_select(idx: int) -> str:
        return f"set_tariff_model_{idx}"

    @staticmethod
    def encode_payment_select(system_name: str, tariff_id: int) -> str:
        return f"set_payments_{system_name}_{tariff_id}"

    @staticmethod
    def decode(key: str) -> ActionCommand:
        for action, pattern, group_names in CallbackCodec._PATTERNS:
            match = pattern.match(key)
            if not match:
                continue
            args = {group_names[i]: match.group(i + 1) for i in range(len(group_names))}
            return ActionCommand(action=action, args=args, raw_key=key)
        return ActionCommand(action="", args={}, raw_key=key)

    @staticmethod
    def get_assistant_id(key: str) -> Optional[int]:
        cmd = CallbackCodec.decode(key)
        if cmd.action != "assistant_select":
            return None
        return int(cmd.args["id"])

