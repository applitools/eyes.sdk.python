import os

import pytest

from applitools.common.utils import general_utils


@pytest.mark.parametrize("env_name, value", [("APPLITOOLS_VAR", "TEST VALUE")])
def test_available_envs_with_get_env_with_prefix(env_name, value):
    assert None is general_utils.get_env_with_prefix(env_name)
    os.environ[env_name] = value
    assert value == general_utils.get_env_with_prefix(env_name)
    del os.environ[env_name]
    os.environ["bamboo_{}".format(env_name)] = value
    assert value == general_utils.get_env_with_prefix(env_name)
    os.environ[env_name + "random"] = value
    assert value == general_utils.get_env_with_prefix("WRONG_KEY", default=value)
    assert "" == general_utils.get_env_with_prefix("WRONG_KEY", default="")
