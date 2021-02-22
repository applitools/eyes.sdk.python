import pytest

from applitools.core import VisualLocator
from tests.utils import parametrize_ids


def test_wrong_visual_locator_names():
    with pytest.raises(ValueError) as exc_info:
        VisualLocator.name([])
        assert exc_info.type == ValueError

    with pytest.raises(ValueError) as exc_info:
        VisualLocator.name(113)
        assert exc_info.type == ValueError

    with pytest.raises(ValueError) as exc_info:
        VisualLocator.names("text", 113)
        assert exc_info.type == ValueError


@pytest.mark.parametrize(
    "name",
    ["Some name", "Create"],
    ids=parametrize_ids("name"),
)
def test_visual_locator_name(name):
    vl = VisualLocator.name(name)
    assert vl.values.names == [name]
    assert vl.values.is_first_only == True
    vl = vl.all()
    assert vl.values.is_first_only == False

    vl = VisualLocator.names(name, name)
    assert vl.values.names == [name, name]

    vl = VisualLocator.names([name, name])
    assert vl.values.names == [name, name]
