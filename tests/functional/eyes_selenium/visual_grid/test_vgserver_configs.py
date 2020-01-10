import pytest

from applitools.common import EyesError
from applitools.selenium import Configuration, Eyes


def test_vgdouble_close_no_check(driver, eyes_runner, batch_info):
    eyes = Eyes(eyes_runner)
    eyes.set_configuration(
        Configuration(app_name="app", test_name="test", batch=batch_info)
    )
    eyes.open(driver)
    with pytest.raises(EyesError) as e:
        eyes.close()
        assert "Eyes not open" in str(e)
