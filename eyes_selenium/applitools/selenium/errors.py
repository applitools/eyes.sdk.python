from selenium.common.exceptions import WebDriverException


class EyesDriverOperationException(WebDriverException):
    """
    Encapsulates an error when trying to perform an action using WebDriver.
    """
