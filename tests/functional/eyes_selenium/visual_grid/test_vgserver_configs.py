from applitools.selenium import Configuration, Eyes


def test_vgdouble_close_no_check(driver, vg_runner, batch_info, fake_connector_class):
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(app_name="app", test_name="test", batch=batch_info)
    )
    eyes.server_connector = fake_connector_class()
    eyes.open(driver)
    eyes.close()
