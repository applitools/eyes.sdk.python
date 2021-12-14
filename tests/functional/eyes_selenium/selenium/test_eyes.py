import pytest

from applitools.common import RectangleSize
from applitools.selenium import Eyes, Target


# @pytest.mark.skip("USDK Difference")
def test_scrollable_modal_on_scrolled_down_page(driver):
    driver.get("https://applitools.github.io/demo/TestPages/ModalsPage")
    eyes = Eyes()
    driver = eyes.open(
        driver,
        "TestModal",
        "ScrollableModalOnScrolledDownPage",
        RectangleSize(width=1024, height=768),
    )
    # Scroll page to the bottom-most paragraph
    driver.execute_script(
        "arguments[0].scrollIntoView()",
        driver.find_element_by_css_selector("body > main > p:nth-child(17)"),
    )
    # Show popup without clicking a button on top to avoid scrolling up
    driver.execute_script("openModal('scrollable_content_modal')")

    content = driver.find_element_by_css_selector(
        ".modal-content.modal-content--scrollable"
    )
    eyes.check(Target.region(content).scroll_root_element(content).fully())

    eyes.close()
