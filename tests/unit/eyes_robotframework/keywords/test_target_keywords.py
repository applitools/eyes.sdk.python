import pytest
from mock import Mock

from EyesLibrary import TargetKeywords

pytestmark = [pytest.mark.skip]


@pytest.fixture()
def target_keyword(eyes_library_with_selenium):
    return TargetKeywords(eyes_library_with_selenium)


def test_target_window(target_keyword):
    target_keyword.target_window()
