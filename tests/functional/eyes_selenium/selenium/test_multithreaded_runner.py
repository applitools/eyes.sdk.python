from __future__ import print_function

from concurrent.futures import ThreadPoolExecutor

import pytest
from selenium import webdriver

from applitools.selenium import ClassicRunner, Eyes, VisualGridRunner


@pytest.mark.parametrize("runner_type", [VisualGridRunner])
def test_ten_threads(runner_type):
    logs_dir = runner_type.get_server_info().logs_dir
    runner = runner_type()

    def perform_test(n):
        with webdriver.Chrome() as driver:
            driver.get("https://applitools.github.io/demo/TestPages/SimpleTestPage/")
            driver.execute_script("window.scrollTo(0,{});".format(n * 55))
            eyes = Eyes(runner)
            try:
                print("Trying to open eyes", n)
                eyes.open(
                    driver,
                    "USDK Tests",
                    "{} Threaded test {}".format(type(runner).__name__, n),
                    {"width": 1024, "height": 768},
                )
                print("Eyes", n, "opened successfully")
                eyes.check_window(fully=False)
                eyes.close_async()
            finally:
                eyes.abort_async()

    with ThreadPoolExecutor(10) as executor:
        list(executor.map(perform_test, range(10)))
    results = runner.get_all_test_results()
    assert len(results) == 10
