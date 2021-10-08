from applitools.selenium import ClassicRunner, VisualGridRunner
from EyesLibrary.eyes import RobotEyes


def test_robot_eyes_agent_id_setup(appium_library, selenium_library):
    eyes = RobotEyes.from_current_library(appium_library, ClassicRunner())
    assert eyes.full_agent_id.startswith("eyes.python.robotframework.appium/")

    eyes = RobotEyes.from_current_library(selenium_library, ClassicRunner())
    assert eyes.full_agent_id.startswith("eyes.python.robotframework.selenium/")

    eyes = RobotEyes.from_current_library(selenium_library, VisualGridRunner())
    assert eyes.full_agent_id.startswith("eyes.python.robotframework.visual_grid/")
