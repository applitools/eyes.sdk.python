from typing import Text, Type, Union

from AppiumLibrary import AppiumLibrary
from SeleniumLibrary import SeleniumLibrary

from applitools.selenium import Eyes as EyesSelenium
from applitools.selenium.selenium_eyes import SeleniumEyes
from applitools.selenium.visual_grid.visual_grid_eyes import VisualGridEyes

from .__version__ import __version__

__all__ = ["RobotEyes"]


class RobotEyes(EyesSelenium):
    @classmethod
    def from_selected_runner(cls, current_library, runner):
        if isinstance(current_library, SeleniumLibrary):
            cls.selenium_eyes_class = RobotEyesSelenium
        elif isinstance(current_library, AppiumLibrary):
            cls.selenium_eyes_class = RobotEyesAppium
        cls.visual_grid_eyes_class = RobotEyesUFG
        return cls(runner)


class RobotEyesSelenium(SeleniumEyes):
    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.python.robotframework.selenium/{version}".format(
            version=__version__
        )


class RobotEyesAppium(SeleniumEyes):
    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.python.robotframework.appium/{version}".format(version=__version__)


class RobotEyesUFG(VisualGridEyes):
    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.python.robotframework.visualgrid/{version}".format(
            version=__version__
        )
