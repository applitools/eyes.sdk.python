import typing as tp

from selenium.common.exceptions import WebDriverException

from applitools.common import logger
from applitools.common.utils.compat import raise_from

if tp.TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

    from applitools.common.utils.custom_types import AnyWebDriver, AnyWebElement
    from applitools.selenium.webdriver import EyesWebDriver


class SwitchToParentIsNotSupported(Exception):
    pass


class EyesWebDriverIsOutOfSync(Exception):
    pass


def ensure_sync_with_underlying_driver(eyes_driver, selenium_driver):
    # type: (EyesWebDriver, WebDriver) -> None
    """
    Checks if frame selected in selenium_driver matches frame_chain in eyes_driver.
    If it doesn't, follows parent frames up to default content and then repeats
    all the chain of frame selections with eyes_driver.
    """
    if not eyes_driver.is_mobile_app:
        try:
            if eyes_driver.frame_chain.size == 0:
                in_sync = _has_no_frame_selected(selenium_driver)
            else:
                selected_frame = eyes_driver.frame_chain.peek
                in_sync = selected_frame.scroll_root_element.is_attached_to_page
        except SwitchToParentIsNotSupported:
            logger.info(
                "Unable to ensure frame chain sync with the underlying driver due to "
                "unsupported 'switch to parent frame' call in the driver"
            )
        if not in_sync:
            try:
                _do_sync_with_underlying_driver(eyes_driver, selenium_driver)
            except Exception as e:
                raise_from(
                    EyesWebDriverIsOutOfSync(
                        "EyesWebDriver frame chain is out of sync. "
                        "Please use web driver returned by Eyes.open call "
                        "for frame switching."
                    ),
                    e,
                )


def _has_no_frame_selected(driver):
    # type: (WebDriver) -> bool
    """
    Predicate that checks if given selenium driver has no frame selected (in other
    words, default content is selected)
    """
    root_element = _current_root_element(driver)
    _swith_to_parent_frame(driver)
    parent_element = _current_root_element(driver)
    if root_element == parent_element:
        return True
    else:
        _switch_to_frame_with_root_element(driver, root_element)
        return False


def _do_sync_with_underlying_driver(eyes_driver, selenium_driver):
    # type: (EyesWebDriver, WebDriverException) -> None
    """
    Goes from currently selected frame in selenium_driver up to
    the topmost default content and remembers the trace.
    Then follows that trace with eyes_driver to get to original frame and have
    frame_chain synchronized.
    """
    root_elements_trace = [_current_root_element(selenium_driver)]
    while True:
        _swith_to_parent_frame(selenium_driver)
        root_element = _current_root_element(selenium_driver)
        if root_element != root_elements_trace[-1]:
            root_elements_trace.append(root_element)
        else:
            root_elements_trace.pop()
            break
    eyes_driver.frame_chain.clear()
    for root_element in reversed(root_elements_trace):
        _switch_to_frame_with_root_element(eyes_driver, root_element)


def _switch_to_frame_with_root_element(driver, root_element):
    # type: (AnyWebDriver, AnyWebElement) -> None
    """
    Tries to find and switch given driver to a frame that has given root_element
    as it's root element.
    """
    for frame in driver.find_elements_by_xpath("//iframe|//frame"):
        driver.switch_to.frame(frame)
        if _current_root_element(driver) == root_element:
            break
        else:
            _swith_to_parent_frame(driver)
    else:
        raise RuntimeError("Failed to reach element {}".format(root_element))


def _current_root_element(driver):
    # type: (WebDriver) -> WebElement
    """
    Finds root WebElement within currently selected frame in given driver.
    Usually it's the 'html' element.
    """
    return driver.find_element_by_xpath("/*")


def _swith_to_parent_frame(driver):
    # type: (WebDriver) -> None
    """
    Switches given driver to the parent frame or raises specific exception
    """
    try:
        driver.switch_to.parent_frame()
    except WebDriverException as e:
        if "Method is not implemented" in e.msg:
            raise_from(SwitchToParentIsNotSupported, e)
        else:
            raise
