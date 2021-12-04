from __future__ import absolute_import

from enum import Enum
from os import getcwd
from typing import Any, List, Optional, Text

from selenium.common.exceptions import StaleElementReferenceException

from .connection import USDKConnection


class Failure(Exception):
    @classmethod
    def check(cls, payload):
        # type: (dict) -> None
        error = payload.get("error")
        if error:
            if error["message"].startswith("stale element reference"):
                raise StaleElementReferenceException(error["message"])
            else:
                raise cls(error["message"], error["stack"])


class ManagerType(Enum):
    VG = "vg"
    CLASSIC = "classic"


class CommandExecutor(object):
    @classmethod
    def create(cls, name, version):
        # type: (Text, Text) -> CommandExecutor
        commands = cls(USDKConnection.create())
        commands.make_sdk(name, version, getcwd())
        return commands

    def __init__(self, connection):
        # type: (USDKConnection) -> None
        self._connection = connection

    def make_sdk(self, name, version, cwd):
        # type: (Text, Text, Text) -> None
        self._connection.notification(
            "Core.makeSDK",
            {"name": name, "version": version, "cwd": cwd, "protocol": "webdriver"},
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

    def manager_close_all_eyes(self, manager, timeout):
        # type: (dict, float) -> List[dict]
        return self._checked_command(
            "EyesManager.closeAllEyes", {"manager": manager}, wait_timeout=timeout
        )

    def eyes_check(self, eyes, settings=None, config=None):
        # type: (dict, Optional[dict], Optional[dict]) -> dict
        payload = {"eyes": eyes}
        if settings is not None:
            payload["settings"] = settings
        if config is not None:
            payload["config"] = config
        return self._checked_command("Eyes.check", payload)

    def eyes_locate(self, eyes, settings, config=None):
        # type: (dict, dict, Optional[dict]) -> dict
        payload = {"eyes": eyes, "settings": settings}
        if config:
            payload["config"] = config
        return self._checked_command("Eyes.locate", payload)

    def eyes_extract_text(self, eyes, regions, config=None):
        # type: (dict, dict, Optional[dict]) -> dict
        payload = {"eyes": eyes, "regions": regions}
        if config:
            payload["config"] = config
        return self._checked_command("Eyes.extractText", payload)

    def eyes_extract_text_regions(self, eyes, settings, config=None):
        # type: (dict, dict, Optional[dict]) -> dict
        payload = {"eyes": eyes, "settings": settings}
        if config:
            payload["config"] = config
        return self._checked_command("Eyes.extractTextRegions", payload)

    def eyes_close_eyes(self, eyes, wait_result):
        # type: (dict, bool) -> List[dict]
        return self._checked_command("Eyes.close", {"eyes": eyes}, wait_result)

    def eyes_abort_eyes(self, eyes, wait_result):
        # type: (dict, bool) -> List[dict]
        return self._checked_command("Eyes.abort", {"eyes": eyes}, wait_result)

    def close(self):
        self._connection.close()

    def _checked_command(self, name, payload, wait_result=True, wait_timeout=9 * 60):
        # type: (Text, dict, bool, float) -> Optional[Any]
        response = self._connection.command(name, payload, wait_result, wait_timeout)
        if wait_result:
            response_payload = response["payload"]
            Failure.check(response_payload)
            return response_payload.get("result")
        else:
            return None
