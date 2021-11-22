from .compat import urldefrag, urljoin, urlparse

__all__ = ("apply_base_url", "is_url_with_scheme", "is_absolute_url")


def is_absolute_url(url):
    return bool(urlparse(url).netloc)


def is_url_with_scheme(url):
    return bool(urlparse(url).scheme)


def apply_base_url(discovered_url, site_base_url, resource_url=None):
    url = urlparse(discovered_url)
    if url.scheme in ["http", "https"] and url.netloc:
        return urldefrag(discovered_url)[0]
    if resource_url and is_url_with_scheme(resource_url):
        site_base_url = resource_url
    return urldefrag(urljoin(site_base_url, discovered_url))[0]
