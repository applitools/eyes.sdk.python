import logging
import time

logger = logging.getLogger(__name__)


def open_webdriver(driver_callable):
    for i in range(5):
        try:
            return driver_callable()
        except Exception:
            logger.exception("Failed to start browser, attempt #%s", i)
            time.sleep(1.0)
    else:
        return driver_callable()
