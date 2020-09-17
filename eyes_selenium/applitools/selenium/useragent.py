from enum import Enum
from typing import Text

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
        origin_ua_string=ua_string,
    )


def to_float(val):
    try:
        return float(val)
    except TypeError:
        return -1


class BrowserNames(Enum):
    Unknown = "Unknown"
    Edge = "Edge"
    IE = "IE"
    Firefox = "Firefox"
    Chrome = "Chrome"
    ChromeMobile = "Chrome Mobile"
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


@attr.s
class UserAgent(object):
    os = attr.ib(default=OSNames.Unknown, converter=OSNames)
    os_major_version = attr.ib(default=-1, converter=to_float)
    os_minor_version = attr.ib(default=-1, converter=to_float)
    browser = attr.ib(default=BrowserNames.Unknown, converter=BrowserNames)
    browser_major_version = attr.ib(default=-1, converter=to_float)
    browser_minor_version = attr.ib(default=-1, converter=to_float)
    origin_ua_string = attr.ib(default=None)

    @property
    def is_internet_explorer(self):
        # type: () -> bool
        return bool(
            self.browser == BrowserNames.IE
            or (self.browser == BrowserNames.Edge and self.browser_major_version <= 18)
        )

    @property
    def is_chrome(self):
        # type: () -> bool
        return self.browser in [
            BrowserNames.Chrome,
            BrowserNames.Chromium,
            BrowserNames.ChromeMobile,
        ]

    @property
    def os_name_with_major_version(self):
        # type: () -> Text
        if self.os_major_version != -1:
            return "{} {:.0f}".format(self.os.value, self.os_major_version)
        return self.os.value
