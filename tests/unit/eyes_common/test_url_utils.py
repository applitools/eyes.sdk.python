import pytest

from applitools.common.utils import apply_base_url
from tests.utils import parametrize_ids


@pytest.mark.parametrize(
    "discovered_url,site_base_url,resource_url,result",
    [
        ["#some", "https://some.com/some", None, "https://some.com/some"],
        ["/some/url", "https://some.com", "/no-host-url", "https://some.com/some/url"],
        ["url", "https://som.com", "https://som.com/yes/", "https://som.com/yes/url"],
    ],
    ids=parametrize_ids("discovered_url,site_base_url,resource_url,result"),
)
def test_apply_base_url(discovered_url, site_base_url, resource_url, result):
    assert apply_base_url(discovered_url, site_base_url, resource_url) == result
