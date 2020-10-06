from pytest import raises

from applitools.core import CheckSettings
from applitools.core.eyes_mixins import merge_check_arguments

_missing_check_settings = "missing 1 required positional argument: 'check_settings'"


def test_merge_check_arguments_empty():
    with raises(TypeError, message=_missing_check_settings):
        merge_check_arguments(CheckSettings)


def test_merge_check_arguments_only_name_keyword():
    with raises(TypeError, message=_missing_check_settings):
        merge_check_arguments(CheckSettings, name="A")


def test_merge_check_arguments_only_name_positional():
    merge_check_arguments(CheckSettings, "A")


def test_merge_check_arguments_only_settings_keyword():
    checks = merge_check_arguments(CheckSettings, check_settings=CheckSettings())

    assert checks == CheckSettings()


def test_merge_check_arguments_only_settings_positional():
    checks = merge_check_arguments(CheckSettings, CheckSettings())

    assert checks == CheckSettings()


def test_merge_check_arguments_both_positional():
    checks = merge_check_arguments(CheckSettings, "A", CheckSettings())

    assert checks == CheckSettings().with_name("A")


def test_merge_check_arguments_both_keyword():
    checks = merge_check_arguments(
        CheckSettings, check_settings=CheckSettings(), name="A"
    )

    assert checks == CheckSettings().with_name("A")


def test_merge_check_arguments_name_valid_settings_none():
    checks = merge_check_arguments(CheckSettings, "A", None)

    assert checks == CheckSettings().with_name("A")


def test_merge_check_arguments_both_none():
    checks = merge_check_arguments(CheckSettings, None, None)

    assert checks == CheckSettings()


def test_merge_check_arguments_name_none_check_settings_valid():
    checks = merge_check_arguments(CheckSettings, None, CheckSettings().with_name("A"))

    assert checks == CheckSettings().with_name("A")


def test_merge_check_arguments_override_name():
    checks = merge_check_arguments(CheckSettings, "A", CheckSettings().with_name("B"))

    assert checks == CheckSettings().with_name("A")
