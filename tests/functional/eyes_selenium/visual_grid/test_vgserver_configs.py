import pytest

from applitools.common import TestFailedError
from applitools.selenium import Configuration, Eyes


def test_vgdouble_close_no_check(driver, vg_runner, batch_info):
    eyes = Eyes(vg_runner)
    eyes.set_configuration(
        Configuration(app_name="app", test_name="test", batch=batch_info)
    )
    eyes.open(driver)
    with pytest.raises(TestFailedError) as e:
        eyes.close()
        assert "Eyes not open" in str(e)
