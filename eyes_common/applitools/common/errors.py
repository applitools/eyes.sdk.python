__all__ = (
    "EyesError",
    "EyesIllegalArgument",
    "OutOfBoundsError",
    "TestFailedError",
    "NewTestError",
    "DiffsFoundError",
    "CoordinatesTypeConversionError",
    "EyesDriverOperationError",
)


class EyesError(Exception):
    """
    Applitools Eyes Exception.
    """


class EyesIllegalArgument(EyesError):
    """
    Raise when parameter with wrong type passed to function
    """


class OutOfBoundsError(EyesError):
    """
    Indicates that an element is outside a specific boundary (e.g, region outside a frame,
    or point outside an image).
    """


class TestFailedError(Exception):
    """
    Indicates that a test did not pass (i.e., test either failed or is a new test).
    """

    def __init__(self, message, test_results=None):
        self.message = message
        self.test_results = test_results

    def __str__(self):
        return "%s , %s" % (self.message, self.test_results)


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


class EyesDriverOperationError(EyesError):
    """
    Encapsulates an error when trying to perform an action using WebDriver.
    """
