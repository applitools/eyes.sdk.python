import pytest

from applitools.core import BatchClose


@pytest.fixture(autouse=True)
def batch_close_enabled(batch_info):
    batch_enabled = BatchClose().set_batch_ids(batch_info.id)
    yield
    batch_enabled.close()


def test_batch_close(eyes, driver):
    eyes.configure.save_new_tests = True
    driver.get("https://demo.applitools.com")
    eyes.open(driver, "TestBatchNotificationApp", "TestBatchClose")
    eyes.check_window()
    eyes.close(False)
