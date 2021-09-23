from typing import Text, Type, Union

from applitools.selenium import Eyes as EyesSelenium

from .__version__ import __version__

__all__ = ["RobotEyesT", "RobotEyesSelenium", "RobotEyesAppium", "RobotEyesUFG"]
RobotEyesT = Type[Union["RobotEyesSelenium", "RobotEyesAppium", "RobotEyesUFG"]]


class RobotEyesSelenium(EyesSelenium):
    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.python.robotframework.selenium/{version}".format(
            version=__version__
        )


class RobotEyesAppium(EyesSelenium):
    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.python.robotframework.appium/{version}".format(version=__version__)


class RobotEyesUFG(EyesSelenium):
    @property
    def base_agent_id(self):
        # type: () -> Text
        return "eyes.python.robotframework.visualgrid/{version}".format(
            version=__version__
        )
