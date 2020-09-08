import logging

from webdriver_manager.chrome import ChromeDriverManager
from mock import patch

from selenium import webdriver
from applitools.selenium import (
    logger,
    Eyes,
    Target,
    ClassicRunner,
)


def test_match_window_data_contains_webapp_domain():
    runner = ClassicRunner()
    eyes = Eyes(runner)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install())
    logger.set_logger(logger.StdoutLogger(level=logging.DEBUG))
    try:
        driver.get("https://demo.applitools.com")
        eyes.open(
            driver, "Demo App", "Test tracking hostname", {"width": 1000, "height": 600}
        )
        with patch(
            "applitools.core.server_connector.ServerConnector.match_window"
        ) as smw:
            eyes.check("Step 1", Target.window().ignore(".auth-header"))
            match_window_data = smw.call_args[0][1]
        assert match_window_data.options.source == "demo.applitools.com"
        eyes.close_async()
    finally:
        driver.quit()
        results = runner.get_all_test_results()
        print(results)
