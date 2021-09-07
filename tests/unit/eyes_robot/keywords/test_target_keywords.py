import pytest
from mock import Mock

from EyesLibrary import TargetKeywords


@pytest.fixture()
def target_keyword():
    return TargetKeywords(Mock())


def test_target_window(target_keyword):
    target_keyword.target_window()
