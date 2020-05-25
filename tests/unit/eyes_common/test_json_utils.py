import pytest

from applitools.common import (
    RenderRequest,
    RGridDom,
    VGResource,
    RenderInfo,
    RunningSession,
)
from applitools.common.selenium import BrowserType
from applitools.common.utils import json_utils


@pytest.mark.parametrize(
    "browser_type",
    [
        BrowserType.CHROME,
        BrowserType.CHROME_ONE_VERSION_BACK,
        BrowserType.CHROME_TWO_VERSIONS_BACK,
        BrowserType.FIREFOX,
        BrowserType.FIREFOX_ONE_VERSION_BACK,
        BrowserType.FIREFOX_TWO_VERSIONS_BACK,
        BrowserType.SAFARI_ONE_VERSION_BACK,
        BrowserType.SAFARI_TWO_VERSIONS_BACK,
    ],
)
def test_render_request_serialize(browser_type):

    request_resources = {"url": VGResource.EMPTY("some-url.com")}
    dom_url = "dom-url.com"
    r_info = RenderInfo(
        width=500,
        height=600,
        size_mode="full-page",
        selector=None,
        region=None,
        emulation_info=None,
    )
    dom = RGridDom(url=dom_url, dom_nodes=[{}], resources=request_resources,)
    requests = [
        RenderRequest(
            webhook="some-webhook.com",
            agent_id="my-agent-id",
            url=dom_url,
            dom=dom,
            resources=request_resources,
            render_info=r_info,
            browser_name=browser_type,
            platform="linux",
            script_hooks=dict(),
            selectors_to_find_regions_for=[],
            send_dom=False,
        )
    ]
    RESULT_PATTERN = '[{"agentId": "my-agent-id", "browser": {"name": "%s", "platform": "linux"}, "dom": {"hash": "a67486a8bc9ba45f878e5b0d8ff9bc68ec6ed9db0382709751327d1793898e16", "hashFormat": "sha256"}, "renderId": null, "renderInfo": {"height": 600, "sizeMode": "full-page", "width": 500}, "resources": {"url": {"contentType": "application/empty-response", "hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "hashFormat": "sha256"}}, "scriptHooks": {}, "selectorsToFindRegionsFor": [], "sendDom": false, "url": "dom-url.com", "webhook": "some-webhook.com"}]'
    assert RESULT_PATTERN % (browser_type.value) == json_utils.to_json(requests)


def test_running_session_serialization_and_deserialization():
    rs = RunningSession(
        id="some-id",
        session_id="session-id",
        batch_id="batch-id",
        baseline_id="baseline_id",
        url="url",
        is_new_session=True,
    )
    rs_json = json_utils.to_json(rs)
    assert '"isNew": true' in rs_json
    assert rs == json_utils.attr_from_json(rs_json, RunningSession)
