from pytest import fixture

from applitools.core import CheckSettings
from applitools.core.eyes_mixins import EyesCheckMixin


class EyesCheckMixinSpy(EyesCheckMixin):
    def __init__(self):
        self.checks = []

    def _check(self, check_settings):
        # type: (*SeleniumCheckSettings) -> Optional[MatchResult]
        self.checks.append(check_settings)
        return "abc"


@fixture
def eyes_check_spy():
    return EyesCheckMixinSpy()


def test_eyes_check_mixin_empty(eyes_check_spy):
    eyes_check_spy.check()

    assert eyes_check_spy.checks == [CheckSettings()]


def test_eyes_check_mixin_only_name_keyword(eyes_check_spy):
    eyes_check_spy.check(name="A")

    assert eyes_check_spy.checks == [CheckSettings().with_name("A")]


def test_eyes_check_mixin_name_positional(eyes_check_spy):
    eyes_check_spy.check("A")

    assert len(eyes_check_spy.checks) == 1
    assert eyes_check_spy.checks == [CheckSettings().with_name("A")]


def test_eyes_check_mixin_check_settings_keyword(eyes_check_spy):
    eyes_check_spy.check(check_settings=CheckSettings())

    assert eyes_check_spy.checks == [CheckSettings()]


def test_eyes_check_mixin_check_settings_positional(eyes_check_spy):
    eyes_check_spy.check(CheckSettings())

    assert eyes_check_spy.checks == [CheckSettings()]


def test_eyes_check_mixin_multiple_checks(eyes_check_spy):
    eyes_check_spy.check(CheckSettings().with_name("A"), CheckSettings().with_name("B"))

    assert eyes_check_spy.checks == [
        CheckSettings().with_name("A"),
        CheckSettings().with_name("B"),
    ]


def test_eyes_check_mixin_override_name(eyes_check_spy):
    eyes_check_spy.check("A", CheckSettings().with_name("B"))

    assert eyes_check_spy.checks == [CheckSettings().with_name("A")]


def test_eyes_check_mixin_override_name(eyes_check_spy):
    eyes_check_spy.check(
        "A", CheckSettings().with_name("B"), CheckSettings().with_name("C")
    )

    assert eyes_check_spy.checks == [
        CheckSettings().with_name("A"),
        CheckSettings().with_name("C"),
    ]


def test_eyes_check_mixin_returns_check_result(eyes_check_spy):
    res = eyes_check_spy.check()

    assert res == "abc"


def test_eyes_check_mixin_returns_check_result(eyes_check_spy):
    res = eyes_check_spy.check(CheckSettings(), CheckSettings())

    assert res is None
