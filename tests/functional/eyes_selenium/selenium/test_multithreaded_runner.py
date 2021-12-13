from concurrent.futures import ThreadPoolExecutor
from os import path, walk

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
                eyes.open(
                    driver,
                    "USDK Tests",
                    "{} Threaded test {}".format(type(runner).__name__, n),
                    {"width": 1024, "height": 768},
                )
                eyes.check_window(fully=False)
                eyes.close(False)
            finally:
                eyes.abort_async()

    try:
        with ThreadPoolExecutor(10) as executor:
            list(executor.map(perform_test, range(10)))
        results = runner.get_all_test_results()
        assert len(results) == 10
    except Exception:
        for root, _, log_files in walk(logs_dir):
            for log_file in log_files:
                log_file = path.join(root, log_file)
                print("Server log file", log_file, "contents")
                with open(log_file) as file:
                    last_lines = file.readlines()[-2000:]
                    print("".join(last_lines))
        raise
