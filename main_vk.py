"""
VK transport entrypoint skeleton.

Business logic lives in ``core.services``; this process should only:
parse VK updates, build ``core.dto.ChannelContext`` / ``InboundEvent``,
call services, and send replies via an implementation of
``core.ports.message_output.MessageOutputPort`` (e.g. ``VkMessageOutput``).
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

