from __future__ import print_function
import time
from contextlib import contextmanager
from functools import wraps
from threading import Thread, Event

from selenium.common.exceptions import WebDriverException


@contextmanager
def hang_logger(interval=60, log_func=print, description="Long operation"):
    canceled = Event()
    start = time.time()

    def watcher():
        while canceled.wait(interval) is not True:
            passed = time.time() - start
            log_func("{} already took {:.1f} seconds".format(description, passed))

    thread = Thread(target=watcher, name="{} watcher".format(description))
    thread.start()
    try:
        yield
    finally:
        canceled.set()
        thread.join()
    passed = time.time() - start
    if passed > interval:
        log_func("{} took {:.1f} seconds to execute".format(description, passed))


def might_hang(interval_or_func=60, log_func=print):
    apply_now = callable(interval_or_func)
    interval = 60 if apply_now else interval_or_func

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            with hang_logger(interval, log_func, func.__name__):
                return func(*args, **kwargs)

        return wrapped

    return decorator(interval_or_func) if apply_now else decorator


@might_hang
def open_webdriver(driver_callable):
    browser = None

    for i in range(5):
        try:
            browser = driver_callable()
            break
        except Exception as e:
            print(
                "Failed to start browser. Retrying {}\n Raised an exception {}".format(
                    i, e
                )
            )
            time.sleep(1.0)

    if browser is None:
        raise WebDriverException("Webdriver wasn't created!")
    return browser
