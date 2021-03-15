import requests


def test_brotli_responses_decoded():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0",
        "Accept-Encoding": "br",
    }

    response = requests.get("https://www.google.com/", headers=headers, verify=False)

    assert response.headers["Content-Encoding"] == "br"
    assert response.content.startswith(b"<")
