import time

import pytest

from applitools.selenium import EyesWebDriver


def test_iframe_selected_with_raw_selenium_driver_is_synced(eyes, driver):
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/index.html")
    eyes_driver = EyesWebDriver(driver, eyes)

    driver.switch_to.frame(0)
    driver.switch_to.frame(0)
    driver.switch_to.frame(0)
    eyes_driver.ensure_sync_with_underlying_driver()

    assert (
        eyes_driver.frame_chain.peek.scroll_root_element.find_element_by_tag_name(
            "body"
        ).get_attribute("class")
        == "friendly"
    )


def test_iframe_unselected_with_raw_selenium_driver_is_synced(eyes, driver):
    driver.get("https://applitools.github.io/demo/TestPages/CorsTestPage/index.html")
    eyes_driver = EyesWebDriver(driver, eyes)

    eyes_driver.switch_to.frame(0)
    driver.switch_to.default_content()
    eyes_driver.ensure_sync_with_underlying_driver()

    assert eyes_driver.frame_chain.peek is None


@pytest.mark.parametrize("i", range(5))
@pytest.mark.parametrize(
    "test_desc,driver_frames,eyes_frames",
    [
        ("No frame selected; sync", [], []),
        ("Frame selected; sync", [], [0]),
        ("Frame selected; out of sync", [0], []),
        ("Far frame selected; sync", [], "far"),
        ("Far frame selected; out of sync", "far", []),
    ],
)
@pytest.mark.parametrize(
    "page_desc,url,far_frame_path,load_time",
    [
        (
            "Light",
            "https://applitools.github.io/demo/TestPages/CorsTestPage/index.html",
            (0, 0),
            1,
        ),
        ("Complex", "https://smiledirectclub.com/invite/", (7, 2), 10),
    ],
)
@pytest.mark.skip("Currently it is designed for manual performance measurement")
def test_measure_ensure_sync_with_underlying_driver_performance(
    driver,
    eyes,
    page_desc,
    url,
    far_frame_path,
    load_time,
    test_desc,
    driver_frames,
    eyes_frames,
    i,
):
    driver_frames = far_frame_path if driver_frames == "far" else driver_frames
    eyes_frames = far_frame_path if eyes_frames == "far" else eyes_frames
    driver.get(url)
    time.sleep(load_time)
    eyes_driver = EyesWebDriver(driver, eyes)
    for n in eyes_frames:
        eyes_driver.switch_to.frame(n)
    for n in driver_frames:
        driver.switch_to.frame(n)
    ts = time.monotonic()
    eyes_driver.ensure_sync_with_underlying_driver()
    r = time.monotonic() - ts
    with open("ensure_sync_with_underlying_driver_perf.txt", "a") as f:
        f.write(
            "{page_desc}; {test_desc}; {i}; {r:.0f}\n".format(
                page_desc=page_desc, test_desc=test_desc, i=i, r=r * 1000
            )
        )
