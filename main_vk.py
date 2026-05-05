"""
VK transport entrypoint skeleton.

This file intentionally contains only wiring placeholders.
Business logic must be reused from core services.
"""

from configure import Settings
from logger import LoggerSingleton


def create_vk_app():
    _setting = Settings()
    _logger = LoggerSingleton.new_instance("logs/log_vk.log")
    _logger.add_info("VK entrypoint initialized (skeleton)")
    return {"settings": _setting, "logger": _logger}


if __name__ == "__main__":
    create_vk_app()

