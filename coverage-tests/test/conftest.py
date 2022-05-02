from itertools import cycle

from selenium.common.exceptions import WebDriverException

from applitools.selenium import BatchInfo, Eyes, StitchMode

from .browsers import *
from .devices import *


@pytest.fixture(scope="session")
def batch_info():
    return BatchInfo("Python Generated tests")


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    # Run all sauce tests in two threads
    sauce_tests = (item for item in items if "sauce_url" in item.fixturenames)
    for test, thread_n in zip(sauce_tests, cycle(range(4))):
        test.add_marker(pytest.mark.xdist_group("sauce_{}".format(thread_n)))


@pytest.fixture(scope="function")
def name_of_test(request):
    return "Python {}".format(request.node.name)


@pytest.fixture(scope="function")
def eyes_runner_class():
    return None


@pytest.fixture(scope="function")
def legacy():
    return False


@pytest.fixture(scope="function")
def execution_grid():
    return False


@pytest.fixture(scope="function")
def sauce_url():
    return "https://{username}:{password}@ondemand.saucelabs.com:443/wd/hub".format(
        username=os.environ["SAUCE_USERNAME"],
        password=os.environ["SAUCE_ACCESS_KEY"],
    )


@pytest.fixture(scope="function")
def driver_builder(chrome):
    return chrome


@pytest.fixture(name="driver", scope="function")
def driver_setup(driver_builder):
    # supported browser types
    #     "Appium": appium,
    #     "Chrome": chrome,
    #     "Firefox": firefox,
    #     "Firefox48": firefox48,
    #     "IE11": ie11,
    #     "Edge": edge,
    #     "Safari11": safari11,
    #     "Safari12": safari12,
    #     "ChromeEmulator": chrome_emulator,
    #

    driver = driver_builder
    yield driver
    # Close the browser.
    try:
        if driver is not None:
            driver.quit()
    except WebDriverException:
        print("Driver was already closed")


@pytest.fixture(name="runner", scope="function")
def runner_setup(eyes_runner_class):
    runner = eyes_runner_class
    yield runner


#     all_test_results = runner.get_all_test_results()
#     print(all_test_results)


@pytest.fixture(scope="function")
def stitch_mode():
    return StitchMode.Scroll


@pytest.fixture(scope="function")
def emulation():
    is_emulation = False
    orientation = ""
    page = ""
    return is_emulation, orientation, page


@pytest.fixture(name="eyes", scope="function")
def eyes_setup(runner, batch_info, stitch_mode, emulation):
    """
    Basic Eyes setup. It'll abort test if wasn't closed properly.
    """
    eyes = Eyes(runner)
    # Initialize the eyes SDK and set your private API key.
    eyes.api_key = os.environ["APPLITOOLS_API_KEY"]
    eyes.configure.batch = batch_info
    eyes.configure.branch_name = "master"
    eyes.configure.parent_branch_name = "master"
    eyes.configure.set_stitch_mode(stitch_mode)
    eyes.configure.set_save_new_tests(False)
    eyes.configure.set_hide_caret(True)
    eyes.configure.set_hide_scrollbars(True)
    is_emulation, orientation, page = emulation
    if is_emulation:
        eyes.add_property("Orientation", orientation)
        eyes.add_property("Page", page)
    yield eyes
    # If the test was aborted before eyes.close was called, ends the test as aborted.
    eyes.abort()
    if runner is not None:
        runner.get_all_test_results(False)
