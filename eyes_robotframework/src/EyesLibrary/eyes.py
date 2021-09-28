from typing import Text, Type, Union

from AppiumLibrary import AppiumLibrary
from SeleniumLibrary import SeleniumLibrary

from applitools.selenium import ClassicRunner
from applitools.selenium import Eyes as EyesSelenium
from applitools.selenium import VisualGridRunner
from applitools.selenium.selenium_eyes import SeleniumEyes
from applitools.selenium.visual_grid.visual_grid_eyes import VisualGridEyes

from .__version__ import __version__

__all__ = ["RobotEyes"]


class RobotEyes(EyesSelenium):
    def __init__(
        self,
        runner,  # type: Union[VisualGridRunner, ClassicRunner]
        selenium_eyes_class,  # type:Type[SeleniumEyes]
        visual_grid_eyes_class,  # type:Type[VisualGridEyes]
    ):
        if selenium_eyes_class is not None:
            self.selenium_eyes_class = selenium_eyes_class
        self.visual_grid_eyes_class = visual_grid_eyes_class
        super(RobotEyes, self).__init__(runner)

    @classmethod
    def from_current_library(cls, current_library, runner):
        if isinstance(current_library, SeleniumLibrary):
            selenium_eyes_class = RobotEyesSelenium
        elif isinstance(current_library, AppiumLibrary):
            selenium_eyes_class = RobotEyesAppium
        else:
            selenium_eyes_class = None
        return cls(runner, selenium_eyes_class, RobotEyesUFG)


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
        return "eyes.python.robotframework.visual_grid/{version}".format(
            version=__version__
        )
