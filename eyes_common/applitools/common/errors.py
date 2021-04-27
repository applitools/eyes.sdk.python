__all__ = (
    "EyesError",
    "OutOfBoundsError",
    "TestFailedError",
    "NewTestError",
    "DiffsFoundError",
    "CoordinatesTypeConversionError",
)


class EyesError(Exception):
    """
    Applitools Eyes Exception.
    """


class OutOfBoundsError(EyesError):
    """
    Indicates that an element is outside a specific boundary (e.g, region outside a frame,
    or point outside an image).
    """


class EyesServiceUnavailableError(EyesError):
    """Indicates that Eyes concurrency limit is exceeded"""


class TestFailedError(Exception):
    """
    Indicates that a test did not pass (i.e., test either failed or is a new test).
    """

    __test__ = False  # avoid warnings in test frameworks

    def __init__(
        self, test_results=None, scenario_id_or_name=None, app_id_or_name=None
    ):
        if all([test_results, scenario_id_or_name, app_id_or_name]):
            msg = "'{}' of '{}'. See details at {}".format(
                scenario_id_or_name, app_id_or_name, test_results.url
            )
            self._test_results = test_results
        else:
            msg = test_results
        super(TestFailedError, self).__init__(msg)


class NewTestError(TestFailedError):
    """
    Indicates that a test is a new test.
    """


class DiffsFoundError(TestFailedError):
    """
    Indicates that an existing test ended, and that differences where found from the baseline.
    """


class CoordinatesTypeConversionError(EyesError):
    def __init__(self, from_, to, test_results=None):
        message = "Cannot convert from {} to {}".format(from_, to)
        super(CoordinatesTypeConversionError, self).__init__(message, test_results)
