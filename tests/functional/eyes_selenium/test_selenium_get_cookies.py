try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import unquote
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import unquote

from threading import Thread

import pytest


class TestServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200, "OK")
        if ":" in self.path:
            key, value = unquote(self.path[1:]).split(":", 1)
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(b"Hello")


@pytest.fixture
def http_server():
    http_server = HTTPServer(("localhost", 8000), TestServer)
    thread = Thread(target=http_server.serve_forever)
    thread.start()
    try:
        yield http_server
    finally:
        http_server.shutdown()
        thread.join()


def test_secure_cookie_is_secure(driver, http_server):
    driver.get("http://127.0.0.1:8000/Set-Cookie: a=b; Secure")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": "127.0.0.1",
            "httpOnly": False,
            "name": "a",
            "path": "/",
            "secure": True,
            "value": "b",
        }
    ]


@pytest.mark.skip("Requirest /etc/hosts file modification")
def test_domain_cookie_with_domain_attr_returns_dotted_domain(driver, http_server):
    driver.get("http://www.example.com:8000/Set-Cookie: a=b; Domain=www.example.com")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": ".www.example.com",
            "httpOnly": False,
            "name": "a",
            "path": "/",
            "secure": False,
            "value": "b",
        }
    ]


def test_domain_http_only(driver, http_server):
    driver.get("http://localhost:8000/Set-Cookie: a=b; HttpOnly")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": "localhost",
            "httpOnly": True,
            "name": "a",
            "path": "/",
            "secure": False,
            "value": "b",
        }
    ]


def test_two_cookies_for_same_domain(driver, http_server):
    driver.get("http://localhost:8000/Set-Cookie: a=b")
    driver.get("http://localhost:8000/Set-Cookie: c=d")

    cookies = driver.get_cookies()

    assert sorted(cookies, key=lambda d: tuple(d[k] for k in sorted(d.keys()))) == [
        {
            "domain": "localhost",
            "httpOnly": False,
            "name": "a",
            "path": "/",
            "secure": False,
            "value": "b",
        },
        {
            "domain": "localhost",
            "httpOnly": False,
            "name": "c",
            "path": "/",
            "secure": False,
            "value": "d",
        },
    ]


def test_two_cookies_for_different_domains(driver, http_server):
    driver.get("http://localhost:8000/Set-Cookie: a=b")
    driver.get("http://127.0.0.1:8000/Set-Cookie: c=d")

    cookies = driver.get_cookies()

    assert cookies == [
        {
            "domain": "127.0.0.1",
            "httpOnly": False,
            "name": "c",
            "path": "/",
            "secure": False,
            "value": "d",
        }
    ]


def test_domain_cookie_with_wrong_domain_dropped(driver, http_server):
    driver.get("http://localhost:8000/Set-Cookie: a=b; Domain=www.example.com")

    cookies = driver.get_cookies()

    assert cookies == []


def test_bad_host_prefix_cookie_is_dropped(driver, http_server):
    driver.get("http://localhost:8000/Set-Cookie: __Host-a=b")

    cookies = driver.get_cookies()

    assert cookies == []


def test_bad_secure_prefix_cookie_is_dropped(driver, http_server):
    driver.get("http://localhost:8000/Set-Cookie: __Secure-a=b")

    cookies = driver.get_cookies()

    assert cookies == []
