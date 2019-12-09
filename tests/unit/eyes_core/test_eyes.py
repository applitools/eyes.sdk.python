from applitools.selenium import Eyes, Configuration


def test_double_eyes_with_new_configuration():
    config = Configuration(test_name="Test1")
    eyes1 = Eyes()
    eyes2 = Eyes()
    eyes1.configuration = config
    config.test_name = "Test2"
    eyes2.configuration = config

    assert eyes1.configuration.test_name == "Test1"


def test_double_eyes_with_configuration_from_eyes():
    eyes1 = Eyes()
    eyes2 = Eyes()
    eyes1.configuration.test_name = "Test1"
    conf = eyes1.configuration
    eyes2.configuration = conf
    eyes2.configuration.test_name = "Test2"
    assert eyes1.configuration.test_name == "Test1"
