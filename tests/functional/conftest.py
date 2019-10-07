import pytest

from applitools.common import StdoutLogger, logger
from applitools.common.utils import iteritems

logger.set_logger(StdoutLogger())


@pytest.fixture(scope="function")
def eyes(request, eyes_class):
    # TODO: allow to setup logger level through pytest option
    # logger.set_logger(StdoutLogger())
    eyes = eyes_class()
    eyes.configuration.hide_scrollbars = True
    eyes.configuration.save_new_tests = False

    # configure eyes options through @pytest.mark.eyes() marker
    eyes_mark_opts = request.node.get_closest_marker("eyes")
    eyes_mark_opts = eyes_mark_opts.kwargs if eyes_mark_opts else {}

    # configure eyes through @pytest.mark.parametrize('eyes', [], indirect=True)
    eyes_parametrized_opts = getattr(request, "param", {})
    if set(eyes_mark_opts.keys()).intersection(eyes_parametrized_opts):
        raise ValueError(
            "Eyes options conflict. The values from .mark.eyes and .mark.parametrize shouldn't intersect."
        )

    eyes_mark_opts.update(eyes_parametrized_opts)
    for key, val in iteritems(eyes_mark_opts):
        setattr(eyes, key, val)

    yield eyes
    eyes.abort()
