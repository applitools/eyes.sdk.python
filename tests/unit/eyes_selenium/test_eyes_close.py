import os

import pytest
from applitools.common import (
    DiffsFoundError,
    EyesError,
    NewTestError,
    TestFailedError,
    TestResults,
)
from applitools.selenium import Eyes
from mock import MagicMock


@pytest.fixture(scope="function")
def eyes():
    return Eyes()


@pytest.fixture(scope="function")
def eyes_opened(eyes, running_session, session_start_info):
    os.environ["APPLITOOLS_API_KEY"] = "SOME KEY"
    eyes._current_eyes._is_opened = True
    eyes._current_eyes._running_session = running_session
    eyes._current_eyes._session_start_info = session_start_info
    eyes._current_eyes._server_connector.stop_session = MagicMock(
        side_effect=lambda *args, **kwargs: TestResults(
            1, 2, 3, 4, 3, 4, 5, 6, 2, status="unresolved"
        )
    )
    return eyes


@pytest.fixture(scope="function")
def eyes_opened_unresolved_new(eyes_opened, started_connector, running_session):
    started_connector.stop_session = MagicMock(
        side_effect=lambda *args, **kwargs: TestResults(
            1, 2, 3, 4, 3, 4, 5, 6, 2, status="unresolved"
        )
    )
    eyes_opened._current_eyes._server_connector = started_connector
    running_session.is_new_session = True
    eyes_opened._current_eyes._running_session = running_session
    return eyes_opened


@pytest.fixture(scope="function")
def eyes_opened_unresolved_old(eyes_opened, started_connector):
    started_connector.stop_session = MagicMock(
        side_effect=lambda *args, **kwargs: TestResults(
            1, 2, 3, 4, 3, 4, 5, 6, 2, status="unresolved"
        )
    )
    eyes_opened._current_eyes._server_connector = started_connector
    return eyes_opened


@pytest.fixture(scope="function")
def eyes_opened_failed(eyes_opened, started_connector):
    started_connector.stop_session = MagicMock(
        side_effect=lambda *args, **kwargs: TestResults(
            1, 2, 3, 4, 3, 4, 5, 6, 2, status="failed"
        )
    )
    eyes_opened._current_eyes._server_connector = started_connector
    return eyes_opened


def test_eyes_close_not_opened(eyes):
    with pytest.raises(EyesError):
        eyes.close()


def test_eyes_close_opened_but_not_session_running(eyes_opened):
    eyes_opened._current_eyes._running_session = None
    test_results = eyes_opened.close()
    assert test_results == TestResults()


def test_eyes_close_old_test_unresolved(eyes_opened_unresolved_old):
    with pytest.raises(DiffsFoundError):
        eyes_opened_unresolved_old.close()


def test_eyes_close_old_test_unresolved_silent(eyes_opened_unresolved_old):
    eyes_opened_unresolved_old.close(False)


def test_eyes_close_new_test_unresolved_should_fail(eyes_opened_unresolved_new):
    eyes_opened_unresolved_new.fail_on_new_test = True

    with pytest.raises(NewTestError):
        eyes_opened_unresolved_new.close(False)


def test_eyes_close_new_test_unresolved(eyes_opened_unresolved_new):
    with pytest.raises(NewTestError):
        eyes_opened_unresolved_new.close()


def test_eyes_close_new_test_unresolved_silent(eyes_opened_unresolved_new):
    eyes_opened_unresolved_new.close(False)


def test_eyes_close_old_test_failed(eyes_opened_failed):
    with pytest.raises(TestFailedError):
        eyes_opened_failed.close()


def test_eyes_close_old_test_failed_silent(eyes_opened_failed):
    eyes_opened_failed.close(False)
