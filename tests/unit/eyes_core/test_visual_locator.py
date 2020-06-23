import pytest

from applitools.common import EyesIllegalArgument
from applitools.core.fluent import VisualLocator


def test_wrong_visual_locator_names():
    with pytest.raises(EyesIllegalArgument) as exc_info:
        VisualLocator.name([])
        assert exc_info.type == EyesIllegalArgument

    with pytest.raises(EyesIllegalArgument) as exc_info:
        VisualLocator.name(113)
        assert exc_info.type == EyesIllegalArgument

    with pytest.raises(EyesIllegalArgument) as exc_info:
        VisualLocator.names("text", 113)
        assert exc_info.type == EyesIllegalArgument


@pytest.mark.parametrize("name", ["Some name", "Create"])
def test_visual_locator_name(name):
    vl = VisualLocator.name(name)
    assert vl.names == [name]

    vl = VisualLocator.names(name, name)
    assert vl.names == [name, name]

    vl = VisualLocator.names([name, name])
    assert vl.names == [name, name]
