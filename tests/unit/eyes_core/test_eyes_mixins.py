from pytest import raises

from applitools.core import CheckSettings
from applitools.core.eyes_mixins import merge_check_arguments


def test_eyes_check_mixin_empty():
    with raises(ValueError, message="Check settings should be provided"):
        merge_check_arguments(CheckSettings)


def test_eyes_check_mixin_only_name_keyword():
    with raises(ValueError, message="Check settings should be provided"):
        merge_check_arguments(CheckSettings, name="A")


def test_eyes_check_mixin_only_name_positional():
    with raises(ValueError, message="Check settings should be provided"):
        merge_check_arguments(CheckSettings, "A")


def test_eyes_check_mixin_check_only_settings_keyword():
    checks = merge_check_arguments(CheckSettings, check_settings=CheckSettings())

    assert checks == CheckSettings()


def test_eyes_check_mixin_check_only_settings_positional():
    checks = merge_check_arguments(CheckSettings, CheckSettings())

    assert checks == CheckSettings()


def test_eyes_check_mixin_check_both_positional():
    checks = merge_check_arguments(CheckSettings, "A", CheckSettings())

    assert checks == CheckSettings().with_name("A")


def test_eyes_check_mixin_check_both_keyword():
    checks = merge_check_arguments(
        CheckSettings, check_settings=CheckSettings(), name="A"
    )

    assert checks == CheckSettings().with_name("A")


def test_eyes_check_mixin_multiple_checks():
    with raises(ValueError, message="Check settings should be provided once"):
        merge_check_arguments(
            CheckSettings,
            CheckSettings().with_name("A"),
            CheckSettings().with_name("B"),
        )


def test_eyes_check_mixin_override_name():
    checks = merge_check_arguments(CheckSettings, "A", CheckSettings().with_name("B"))

    assert checks == CheckSettings().with_name("A")
