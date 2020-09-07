from applitools.common import VisualGridOption
from applitools.selenium.visual_grid import RunningTest


def test_running_test_options_none_none():
    options = RunningTest._options_dict(None, None)

    assert options == {}


def test_running_test_options_dict_none_one():
    options = RunningTest._options_dict(None, (VisualGridOption("key", "val"),))

    assert options == {"key": "val"}


def test_running_test_options_dict_one_one_combined():
    options = RunningTest._options_dict(
        (VisualGridOption("key1", "val1"),), (VisualGridOption("key2", "val2"),)
    )

    assert options == {"key1": "val1", "key2": "val2"}


def test_running_test_options_dict_values_updated_values():
    options = RunningTest._options_dict(
        (VisualGridOption("key1", "val1"), VisualGridOption("key2", "val2")),
        (VisualGridOption("key1", "val3"), VisualGridOption("key4", "val4")),
    )

    assert options == {"key1": "val3", "key2": "val2", "key4": "val4"}
