import os

from mock import patch

from applitools.common import Configuration


def test_config_envs():
    with patch.dict(
        os.environ,
        {
            "APPLITOOLS_BRANCH": "name",
            "APPLITOOLS_PARENT_BRANCH": "parent branch",
            "APPLITOOLS_BASELINE_BRANCH": "baseline branch",
            "APPLITOOLS_API_KEY": "api key",
            "APPLITOOLS_SERVER_URL": "server url",
        },
    ):
        config = Configuration()
    assert config.branch_name == "name"
    assert config.parent_branch_name == "parent branch"
    assert config.baseline_branch_name == "baseline branch"
    assert config.api_key == "api key"
    assert config.server_url == "server url"
