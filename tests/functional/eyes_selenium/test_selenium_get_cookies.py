import time
from threading import Thread

import pytest

try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import unquote
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import unquote


class TestServer(HTTPServer):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200, "OK")
            for header in self.server.headers:
                self.send_header(*header)
            self.end_headers()
            self.wfile.write(b"Hello")

    def __init__(self):
        # HTTPServer is an old-style class
        HTTPServer.__init__(self, ("localhost", 8000), TestServer.Handler)
        self.headers = []


@pytest.fixture
def http_server():
    http_server = TestServer()
    thread = Thread(target=http_server.serve_forever)
    thread.start()
    try:
        yield http_server
    finally:
        http_server.shutdown()
        thread.join()


def test_expiring_cookie_max_age(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b; Max-Age=60")]
    expiry = int(time.time() + 60)
    driver.get("http://localhost:8000/")

    cookie = driver.get_cookies()[0]

    assert cookie.pop("expiry") - expiry < 1
    assert cookie == {
        "domain": "localhost",
        "httpOnly": False,
        "name": "a",
        "path": "/",
        "secure": False,
        "value": "b",
    }


def test_expiring_cookie_timestamp(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b; Expires=Fri, 1 Jan 2100 01:01:01 GMT")]
    driver.get("http://localhost:8000/")

    cookie = driver.get_cookies()[0]

    assert cookie == {
        "domain": "localhost",
        "expiry": 4102448461,
        "httpOnly": False,
        "name": "a",
        "path": "/",
        "secure": False,
        "value": "b",
    }


def test_expired_cookie(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b; Expires=Thu, 1 Jan 1970 00:00:00 GMT")]
    driver.get("http://localhost:8000/")

    cookies = driver.get_cookies()

    assert cookies == []


def test_secure_cookie_is_secure(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b; Secure")]
    driver.get("http://localhost:8000/")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": "localhost",
            "httpOnly": False,
            "name": "a",
            "path": "/",
            "secure": True,
            "value": "b",
        }
    ]


def test_domain_cookie_with_domain_attr_returns_dot_domain(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b; Domain=www.localtest.me")]
    driver.get("http://www.localtest.me:8000/")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": ".www.localtest.me",
            "httpOnly": False,
            "name": "a",
            "path": "/",
            "secure": False,
            "value": "b",
        }
    ]


def test_domain_cookie_with_dot_domain_attr_returns_dot_domain(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b; Domain=.www.localtest.me")]
    driver.get("http://www.localtest.me:8000/")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": ".www.localtest.me",
            "httpOnly": False,
            "name": "a",
            "path": "/",
            "secure": False,
            "value": "b",
        }
    ]


def test_domain_cookie_with_top_domain_attr(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b; Domain=localtest.me")]
    driver.get("http://www.localtest.me:8000/")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": ".localtest.me",
            "httpOnly": False,
            "name": "a",
            "path": "/",
            "secure": False,
            "value": "b",
        }
    ]


def test_domain_http_only(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b; HttpOnly")]
    driver.get("http://www.localtest.me:8000/")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": "www.localtest.me",
            "httpOnly": True,
            "name": "a",
            "path": "/",
            "secure": False,
            "value": "b",
        }
    ]


def test_two_cookies_for_same_domain(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b")]
    driver.get("http://www.localtest.me:8000/a")
    http_server.headers = [("Set-Cookie", "c=d")]
    driver.get("http://www.localtest.me:8000/c")

    cookies = driver.get_cookies()

    assert sorted(cookies, key=lambda d: tuple(d[k] for k in sorted(d.keys()))) == [
        {
            "domain": "www.localtest.me",
            "httpOnly": False,
            "name": "a",
            "path": "/",
            "secure": False,
            "value": "b",
        },
        {
            "domain": "www.localtest.me",
            "httpOnly": False,
            "name": "c",
            "path": "/",
            "secure": False,
            "value": "d",
        },
    ]


def test_two_cookies_for_different_domains(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b")]
    driver.get("http://www.localtest.me:8000/a")
    http_server.headers = [("Set-Cookie", "c=d")]
    driver.get("http://vvv.localtest.me:8000/c")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": "vvv.localtest.me",
            "httpOnly": False,
            "name": "c",
            "path": "/",
            "secure": False,
            "value": "d",
        }
    ]


def test_domain_cookie_with_wrong_domain_dropped(driver, http_server):
    http_server.headers = [("Set-Cookie", "a=b; Domain=www.example.com")]
    driver.get("http://www.localtest.me:8000/")

    cookies = driver.get_cookies()

    assert cookies == []


def test_bad_host_prefix_cookie_is_dropped(driver, http_server):
    http_server.headers = [("Set-Cookie", "__Host-a=b")]
    driver.get("http://www.localtest.me:8000/")

    cookies = driver.get_cookies()

    assert cookies == []


def test_bad_secure_prefix_cookie_is_dropped(driver, http_server):
    http_server.headers = [("Set-Cookie", "__Secure-a=b")]
    driver.get("http://www.localtest.me:8000/")

    cookies = driver.get_cookies()

    assert cookies == []
