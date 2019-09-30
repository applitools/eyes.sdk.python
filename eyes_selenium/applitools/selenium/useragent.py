from enum import Enum

import attr
from ua_parser import user_agent_parser

__all__ = ("parse_user_agent_string", "BrowserNames", "OSNames", "UserAgent")


def parse_user_agent_string(ua_string):
    # type: (str) -> UserAgent
    parsed = user_agent_parser.Parse(ua_string)
    ua = parsed["user_agent"]
    os = parsed["os"]
    try:
        browser_name = BrowserNames(ua["family"])
    except ValueError:
        browser_name = BrowserNames.Unknown
    try:
        os_name = OSNames(os["family"])
    except ValueError:
        os_name = OSNames.Unknown
    return UserAgent(
        os=os_name,
        os_major_version=os["major"],
        os_minor_version=os["minor"],
        browser=browser_name,
        browser_major_version=ua["major"],
        browser_minor_version=ua["minor"],
    )


def to_float(val):
    try:
        return float(val)
    except TypeError:
        return -1


@attr.s
class UserAgent(object):
    os = attr.ib()
    os_major_version = attr.ib(converter=to_float)
    os_minor_version = attr.ib(converter=to_float)
    browser = attr.ib()
    browser_major_version = attr.ib(converter=to_float)
    browser_minor_version = attr.ib(converter=to_float)


class BrowserNames(Enum):
    Unknown = "Unknown"
    Edge = "Edge"
    IE = "IE"
    Firefox = "Firefox"
    Chrome = "Chrome"
    HeadlessChrome = "HeadlessChrome"
    Safari = "Safari"
    Chromium = "Chromium"
    MobileSafari = "Mobile Safari"


class OSNames(Enum):
    Unknown = "Unknown"
    Windows = "Windows"
    IOS = "iOS"
    Macintosh = "Macintosh"
    ChromeOS = "ChromeOS"
    Android = "Android"
    Linux = "Linux"
