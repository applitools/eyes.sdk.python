from concurrent.futures import ThreadPoolExecutor

import pytest
from selenium import webdriver

from applitools.selenium import ClassicRunner, Eyes, VisualGridRunner


@pytest.mark.parametrize("runner_type", [ClassicRunner, VisualGridRunner])
def test_five_threads(runner_type):
    runner = runner_type()

    def perform_test(n):
        with webdriver.Chrome() as driver:
            driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/")
            driver.execute_script("window.scrollTo(0,{});".format(n * 55))
            eyes = Eyes(runner)
            try:
                eyes.open(
                    driver,
                    "USDK Tests",
                    "{} Threaded test {}".format(runner_type.__name__, n),
                    {"width": 1024, "height": 768},
                )
                eyes.check_window(fully=False)
                eyes.close_async()
            finally:
                eyes.abort_async()

    executor = ThreadPoolExecutor(5)
    list(executor.map(perform_test, range(5)))
    results = runner.get_all_test_results()
    assert len(results) == 5
