from applitools.selenium import Configuration, Eyes


def test_double_eyes_with_new_configuration():
    config = Configuration(test_name="Test1")
    eyes1 = Eyes()
    eyes2 = Eyes()
    eyes1.set_configuration(config)
    config.test_name = "Test2"
    eyes2.set_configuration(config)

    assert eyes1.configure.test_name == "Test1"
    assert eyes2.configure.test_name == "Test2"


def test_double_eyes_with_configuration_from_eyes():
    eyes1 = Eyes()
    eyes2 = Eyes()
    eyes1.configure.test_name = "Test1"
    conf = eyes1.configure
    eyes2.set_configuration(conf)
    eyes2.configure.test_name = "Test2"
    assert eyes1.configure.test_name == "Test1"
    assert eyes2.configure.test_name == "Test2"


def test_get_set_configuration():
    eyes = Eyes()
    conf = eyes.get_configuration()
    assert conf.server_url == "https://eyesapi.applitools.com"
    assert id(conf) != id(eyes.configure)
    conf.test_name = "Test1"
    assert eyes.configure.test_name != "Test1"
    eyes.set_configuration(conf)
    assert eyes.configure.test_name == "Test1"
    assert id(eyes.configure) != conf


def test_same_config_with_no_batch_with_multiple_eyes():
    conf = Configuration().set_app_name("boodleAI").set_test_name("Test 5")
    eyes1 = Eyes()
    eyes2 = Eyes()
    eyes1.set_configuration(conf)
    eyes2.set_configuration(conf)
    assert eyes1.configure.batch
    assert eyes2.configure.batch
    assert eyes1.configure.batch == eyes2.configure.batch
