from .compat import urlparse, urljoin

__all__ = ("apply_base_url", "is_url_with_scheme", "is_absolute_url")


def is_absolute_url(url):
    return bool(urlparse(url).netloc)


def is_url_with_scheme(url):
    return bool(urlparse(url).scheme)


def apply_base_url(discovered_url, base_url, resource_url=None):
    url = urlparse(discovered_url)
    if url.scheme in ["http", "https"] and url.netloc:
        return discovered_url
    if resource_url:
        base_url = resource_url
    return urljoin(base_url, discovered_url)
