from applitools.selenium import Eyes
from EyesLibrary.base import RobotMobileNativeRunner, RobotWebRunner, RobotWebUFGRunner


def test_robot_eyes_agent_id_setup(appium_library, selenium_library):
    eyes = Eyes(RobotMobileNativeRunner())
    assert eyes.full_agent_id.startswith("eyes.python.robotframework.appium/")

    eyes = Eyes(RobotWebRunner())
    assert eyes.full_agent_id.startswith("eyes.python.robotframework.selenium/")

    eyes = Eyes(RobotWebUFGRunner())
    assert eyes.full_agent_id.startswith("eyes.python.robotframework.visual_grid/")
