import json
import os
import time
from collections import OrderedDict

import pytest
from mock import MagicMock
from selenium.webdriver.common.by import By

from applitools.common import Point
from applitools.selenium import Eyes, EyesWebDriver, eyes_selenium_utils
from applitools.selenium.capture import dom_capture


@pytest.fixture(scope="function")
def eyes_for_class(request, eyes_opened):
    # TODO: implement eyes.setDebugScreenshotsPrefix("Java_" + testName + "_");

    request.cls.eyes = eyes_opened
    request.cls.driver = eyes_opened.driver
    yield


@pytest.fixture(scope="function")
def driver_for_class(request, driver):
    viewport_size = request.node.get_closest_marker("viewport_size").args[0]

    driver = EyesWebDriver(driver, MagicMock(Eyes))
    driver.quit = MagicMock()
    if viewport_size:
        eyes_selenium_utils.set_browser_size(driver, viewport_size)
    request.cls.driver = driver

    yield
    driver.quit()


@pytest.mark.usefixtures("driver_for_class")
@pytest.mark.browser("chrome")
@pytest.mark.viewport_size({"width": 800, "height": 600})
class TestDomCaptureUnit(object):
    cur_dir = os.path.abspath(__file__).rpartition("/")[0]
    samples_dir = os.path.join(cur_dir, "resources")

    def _get_expected_json(self, test_name):
        with open(os.path.join(self.samples_dir, test_name + ".json"), "r") as f:
            return json.loads(f.read(), object_pairs_hook=OrderedDict)

    @pytest.mark.test_page_url(
        "https://applitools-dom-capture-origin-1.surge.sh/test.html"
    )
    @pytest.mark.skip
    def test_send_dom_simple_HTML(self):
        actual_dom_json = dom_capture.get_full_window_dom(
            self.driver, return_as_dict=True
        )
        expected_dom_json = self._get_expected_json("test_send_dom_simple_HTML")

        assert actual_dom_json["tagName"] == expected_dom_json["tagName"]
        assert actual_dom_json.keys() == expected_dom_json.keys()
        assert sorted(actual_dom_json["rect"].keys()) == sorted(
            expected_dom_json["rect"].keys()
        )
        assert actual_dom_json["style"] == expected_dom_json["style"]
        assert len(actual_dom_json["childNodes"]) == len(
            expected_dom_json["childNodes"]
        )
        assert (
            actual_dom_json["childNodes"][0]["tagName"]
            == expected_dom_json["childNodes"][0]["tagName"]
        )
        assert (
            actual_dom_json["childNodes"][-1]["tagName"]
            == expected_dom_json["childNodes"][-1]["tagName"]
        )

    @pytest.mark.test_page_url(
        "https://booking.kayak.com/flights/TLV-MIA/2018-11-15/2019-04-31?sort=bestflight_a"
    )
    def test_dom_capture_speed(self):
        # now = dt.datetime.now()
        # cur_date = now.strftime("%Y-%m-%d")  # 2018-10-14
        # month_ahead = (now + dt.timedelta(days=30)).strftime("%Y-%m-%d")  # 2018-11-14
        start = time.time()
        dom_json = dom_capture.get_full_window_dom(self.driver)  # noqa: F841
        end = time.time()
        print("TOOK {} ms".format((end - start) * 1000))

    @pytest.mark.test_page_url(
        "http://applitools.github.io/demo/TestPages/DomTest/dom_capture.html"
    )
    def test_send_dom1(self):
        expected_json = self._get_expected_json("test_send_dom1")
        dom_json = dom_capture.get_full_window_dom(self.driver, return_as_dict=True)
        assert dom_json["css"] == expected_json["css"]

    @pytest.mark.test_page_url(
        "http://applitools.github.io/demo/TestPages/DomTest/dom_capture_2.html"
    )
    def test_send_dom2(self):
        expected_json = self._get_expected_json("test_send_dom2")
        dom_json = dom_capture.get_full_window_dom(self.driver, return_as_dict=True)
        assert dom_json["css"] == expected_json["css"]

    @pytest.mark.test_page_url(
        "https://www.booking.com/searchresults.en-gb.html?label=gen173nr"
        "-1FCAEoggJCAlhYSDNYBGhqiAEBmAEuwgEKd2luZG93cyAxMMgBDNgBAegBAfgBC5ICAXmoAgM;sid"
        "=ce4701a88873eed9fbb22893b9c6eae4;city=-2600941;from_idr=1&;ilp=1;d_dcp=1"
    )
    def test_send_dom_booking1(self):
        dom_json = dom_capture.get_full_window_dom(self.driver)  # noqa: F841

    @pytest.mark.test_page_url(
        "https://booking.kayak.com/flights/TLV-MIA/2018-09-25/2018-10-31?sort=bestflight_a"
    )
    def test_send_dom_booking2(self):
        dom_json = dom_capture.get_full_window_dom(self.driver)  # noqa: F841

    @pytest.mark.test_page_url(
        "https://www.bestbuy.com/site/apple-macbook-pro-13-display-intel-core-i5-8-gb-memory-256gb-flash-storage"
        "-silver/6936477.p?skuId=6936477"
    )
    def test_send_dom_bestbuy1(self):
        try:
            self.driver.find_elements_by_css_selector(".us-link")[0].element.click()
        except IndexError:
            # click isn't required
            pass
        start = time.time()
        dom_json = dom_capture.get_full_window_dom(self.driver)  # noqa: F841
        end = time.time()
        print("TOOK {} ms".format((end - start) * 1000))

    @pytest.mark.test_page_url(
        "https://nikita-andreev.github.io/applitools/dom_capture.html?aaa"
    )
    def test_send_dom_nsa(self):
        expected_json = self._get_expected_json("test_send_dom_nsa")
        dom_json = dom_capture.get_full_window_dom(self.driver, return_as_dict=True)
        assert dom_json["css"] == expected_json["css"]

        def inner_css(o):
            return o["childNodes"][1]["childNodes"][3]["childNodes"][0]["css"]

        assert inner_css(dom_json) == inner_css(expected_json)

    @pytest.mark.test_page_url(
        "https://nikita-andreev.github.io/applitools/dom_capture.html?aaa"
    )
    def test_position_scrolled_to_origin_after_traversing(self):
        # Page must contain scrolling
        dom_json = dom_capture.get_full_window_dom(self.driver)  # noqa: F841
        current_scroll = eyes_selenium_utils.get_current_position(
            self.driver, self.driver.find_element_by_tag_name("html")
        )
        assert current_scroll == Point(0, 0)


@pytest.mark.usefixtures("eyes_for_class")
@pytest.mark.test_suite_name("Eyes Selenium SDK - DynamicPages")
@pytest.mark.viewport_size({"width": 1200, "height": 800})
@pytest.mark.skip("Only for local testing because changes always")
class TestDynamicPages(object):
    @pytest.mark.test_page_url("https://www.nbcnews.com/")
    @pytest.mark.eyes_config(send_dom=True, force_full_page_screenshot=True)
    def test_nbc_news(self):
        self.eyes.check_window("NBC News Test")

    @pytest.mark.test_page_url("https://www.ebay.com/")
    @pytest.mark.eyes_config(send_dom=True, force_full_page_screenshot=True)
    def test_ebay(self):
        self.eyes.check_window("ebay Test")
        self.driver.find_element(by=By.LINK_TEXT, value="Electronics").click()
        self.eyes.check_window("ebay Test - Electroincs")
        self.driver.find_element(by=By.LINK_TEXT, value="Smart Home").click()
        self.eyes.check_window("ebay Test - Electroincs > Smart Home")

    @pytest.mark.test_page_url("https://www.aliexpress.com/")
    @pytest.mark.eyes_config(send_dom=True, force_full_page_screenshot=True)
    def test_aliexpress(self):
        self.eyes.check_window("AliExpress Test")

    @pytest.mark.test_page_url(
        "https://www.bestbuy.com/site/apple-macbook-pro-13-display-intel-core-i5-8-gb-memory-256gb-flash-storage"
        "-silver/6936477.p?skuId=6936477"
    )
    @pytest.mark.eyes_config(send_dom=True, force_full_page_screenshot=True)
    def test_bestbuy(self):
        self.driver.find_elements(by=By.CSS_SELECTOR, value=".us-link")[0].click()
        self.eyes.check_window("BestBuy Test")


@pytest.mark.usefixtures("eyes_for_class")
@pytest.mark.test_suite_name("Eyes Selenium SDK - CustomersPages")
@pytest.mark.viewport_size({"width": 1200, "height": 800})
@pytest.mark.skip("Only for local testing because changes always")
class TestCustomersPages(object):
    @pytest.mark.test_page_url(
        "https://www.amazon.com/stream/cd7be774-51ef-4dfe-8e97-1fdec7357113/ref=strm_theme_kitchen?asCursor"
        "=WyIxLjgiLCJ0czEiLCIxNTM1NTQyMjAwMDAwIiwiIiwiUzAwMTc6MDpudWxsIiwiUzAwMTc6MjoxIiwiUzAwMTc6MDotMSIsIiIsIiIsIjAiLCJzdWI0IiwiMTUzNTU5NDQwMDAwMCIsImhmMS1zYXZlcyIsIjE1MzU2MDE2MDAwMDAiLCJ2MSIsIjE1MzU2MDUyMDQyMzgiLCIiLCIwIiwidjEiLCIxNTM1NTg1NDAwMDAwIl0%3D&asCacheIndex=0&asYOffset=-321&asMod=1"
    )
    @pytest.mark.eyes_config(send_dom=True)
    def test_amazon_special_page(self):
        self.eyes.check_window("Amazon")

    @pytest.mark.test_page_url(
        "https://www.staples.com/Staples-Manila-File-Folders-Letter-3-Tab-Assorted-Position-100-Box/product_116657"
    )
    @pytest.mark.eyes_config(send_dom=True)
    def test_staples_special_page(self):
        self.eyes.check_window("Staples")

    @pytest.mark.test_page_url(
        "https://www.booking.com/searchresults.en-gb.html?label=gen173nr"
        "-1FCAEoggJCAlhYSDNYBGhqiAEBmAEuwgEKd2luZG93cyAxMMgBDNgBAegBAfgBC5ICAXmoAgM;sid"
        "=ce4701a88873eed9fbb22893b9c6eae4;city=-2600941;from_idr=1&;ilp=1;d_dcp=1"
    )
    @pytest.mark.eyes_config(send_dom=True)
    def test_booking_special_page(self):
        self.eyes.check_window("Booking")

    @pytest.mark.test_page_url(
        "https://www.games-workshop.com/en-US/The-Beast-Arises-Omnibus-1-2018"
    )
    @pytest.mark.eyes_config(send_dom=True)
    def test_game_workshop_special_page(self):
        self.eyes.check_window("Games Workshop")

    @pytest.mark.eyes_config(send_dom=True, force_full_page_screenshot=True)
    @pytest.mark.viewport_size({"width": 800, "height": 600})
    @pytest.mark.test_page_url(
        "https://nikita-andreev.github.io/applitools/dom_capture.html?aaa"
    )
    def test_nikita_example(self):
        self.eyes.check_window("Nikita")


def test_efficient_string_replace():
    assert (
        efficient_string_replace(
            "@<",
            ">#",
            "abcdef@<0>#ghijklmnop@<1>#qrstuv@<2>#wx@<1>#@<0>#yz",
            {"0": "ABCDEFG", "1": "HIJKLMNOP", "2": "QRSTUV", "3": "WXYZ"},
        )
        == "abcdefABCDEFGghijklmnopHIJKLMNOPqrstuvQRSTUVwxHIJKLMNOPABCDEFGyz"
    )


def test_clean_for_json():
    assert clean_for_json("\b\t\n\f\r") == r"\b\t\n\f\r"
    assert clean_for_json('"/') == r"\"/"
    assert clean_for_json("\\") == r"\\"
    assert clean_for_json(chr(25)) == r"\u0019"
