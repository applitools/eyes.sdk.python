from copy import deepcopy
from enum import Enum
from typing import Any, List, Optional, Text

from .connection import USDKConnection

SDK_NAME = "eyes.sdk.python"


class Failure(Exception):
    @classmethod
    def check(cls, payload):
        # type: (dict) -> None
        error = payload.get("error")
        if error:
            raise cls(error["message"], error["stack"])


class ManagerType(Enum):
    VG = "vg"
    CLASSIC = "classic"


class CommandExecutor(object):
    def __init__(self, connection):
        # type: (USDKConnection) -> None
        self._connection = connection

    def session_init(self):
        # type: () -> None
        self._connection.notification(
            "Session.init", {"name": SDK_NAME, "version": "1", "protocol": "webdriver"}
        )

    def core_make_manager(self, manager_type, concurrency=None, is_legacy=None):
        # type: (ManagerType, Optional[int], Optional[bool]) -> dict
        payload = {"type": manager_type.value}
        if concurrency is not None:
            payload["concurrency"] = concurrency
        if is_legacy is not None:
            payload["legacy"] = is_legacy
        return self._checked_command("Core.makeManager", payload)

    def core_get_viewport_size(self, driver):
        # type (dict) -> dict
        return self._checked_command("Core.getViewportSize", {"driver": driver})

    def core_set_viewport_size(self, driver, size):
        # type (dict, dict) -> None
        self._checked_command("Core.setViewportSize", {"driver": driver, "size": size})

    def manager_open_eyes(self, manager, driver, config=None):
        # type: (dict, dict, Optional[dict]) -> dict
        payload = {"manager": manager, "driver": driver}
        if config is not None:
            payload["config"] = config
        return self._checked_command("EyesManager.openEyes", payload)

    def manager_close_all_eyes(self, manager):
        # type: (dict) -> List[dict]
        return self._checked_command("EyesManager.closeAllEyes", {"manager": manager})

    def eyes_check(self, eyes, settings=None, config=None):
        # type: (dict, Optional[dict], Optional[dict]) -> dict
        payload = {"eyes": eyes}
        if settings is not None:
            payload["settings"] = settings
        if config is not None:
            payload["config"] = config
        return self._checked_command("Eyes.check", payload)

    def eyes_close_eyes(self, eyes):
        # type: (dict) -> List[dict]
        return self._checked_command("Eyes.close", {"eyes": eyes})

    def eyes_abort_eyes(self, eyes):
        # type: (dict) -> List[dict]
        return self._checked_command("Eyes.abort", {"eyes": eyes})

    def _checked_command(self, name, payload):
        # type: (Text, dict) -> Optional[Any]
        response = self._connection.command(name, payload)
        response_payload = response["payload"]
        Failure.check(response_payload)
        return response_payload.get("result")
