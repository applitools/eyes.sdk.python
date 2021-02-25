import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from applitools.common import Region
from applitools.selenium import Target

pytestmark = [
    pytest.mark.platform("Linux"),
    pytest.mark.viewport_size({"width": 700, "height": 460}),
]


def test_check_window_with_match_region_paddings__fluent(
    eyes_opened, check_test_result
):
    eyes_opened.check(
        "Fluent - Window with ignore region by selector stretched",
        Target.window()
        .fully()
        .ignore(".ignore", padding=dict(left=10))
        .content("#stretched", padding=dict(top=10))
        .layout("#centered", padding=dict(top=10, right=50))
        .strict("overflowing-div", padding=dict(bottom=100)),
    )
    check_test_result.send(
        [
            {
                "actual_name": "ignore",
                "expected": [
                    Region(10 + 10, 286, 800, 500),
                    Region(122 + 10, 933, 456, 306),
                    Region(8 + 10, 1277, 690, 206),
                ],
            }
        ]
    )


@pytest.mark.test_page_url(
    "https://applitools.github.io/demo/TestPages/VisualGridTestPage/duplicates.html"
)
@pytest.mark.test_suite_name("Eyes Selenium SDK - Duplicates")
def test_duplicatedIFrames(eyes_opened):
    eyes_opened.driver.switch_to.frame(2)
    wait = WebDriverWait(eyes_opened.driver, 30)
    wait.until(EC.visibility_of_element_located((By.ID, "p2")))
    eyes_opened.driver.switch_to.default_content()
    eyes_opened.check_window("Duplicated Iframes")
