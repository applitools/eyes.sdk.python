"""
Pytest configuration

pytest |-n|--platform|--browser|--headless

Example of usage:
    pytest -n 5     # run tests on all supported platforms in 5 thread
    pytest --platform 'iPhone 10.0'  # run tests only for iPhone 10.0 platform in one thread
    pytest --platform 'Linux' --browser firefox    # run all tests on Linux platform with firefox browser
    pytest --browser firefox    # run all tests on your current platform with firefox browser
    pytest --browser firefox --headless 1   # run all tests on your current platform with firefox browser in headless mode
"""
import pytest
from applitools.core import StdoutLogger, logger
from applitools.core.utils import iteritems

logger.set_logger(StdoutLogger())


@pytest.fixture(scope="function")
def eyes(request, eyes_class):
    # TODO: allow to setup logger level through pytest option
    # logger.set_logger(StdoutLogger())
    eyes = eyes_class()
    eyes.hide_scrollbars = True

    # configure eyes options through @pytest.mark.eyes() marker
    eyes_mark_opts = request.node.get_closest_marker("eyes")
    eyes_mark_opts = eyes_mark_opts.kwargs if eyes_mark_opts else {}

    # configure eyes through @pytest.mark.parametrize('eyes', [])
    eyes_parametrized_opts = getattr(request, "param", {})
    if set(eyes_mark_opts.keys()).intersection(eyes_parametrized_opts):
        raise ValueError(
            "Eyes options conflict. The values from .mark.eyes and .mark.parametrize shouldn't intersect."
        )

    eyes_mark_opts.update(eyes_parametrized_opts)
    for key, val in iteritems(eyes_mark_opts):
        setattr(eyes, key, val)

    yield eyes
    eyes.abort_if_not_closed()
