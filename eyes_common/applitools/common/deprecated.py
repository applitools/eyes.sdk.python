import typing as tp
import warnings
from functools import wraps
from inspect import getcallargs


def module(name, recommendation):
    # type: (tp.Text, tp.Text) -> None
    message = "Module {} is deprecated: {}".format(name, recommendation)
    warnings.warn(message, stacklevel=2, category=ImportWarning)


def argument(name, recommendation):
    # type: (tp.Text, tp.Text) -> tp.Callable[[tp.Callable], tp.Callable]
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            call_args = getcallargs(func, *args, **kwargs)
            argval = call_args.get(name)
            if argval is not None:
                message = "Argument {} of {} is deprecated: {}".format(
                    name, func.__name__, recommendation
                )
                warnings.warn(message, stacklevel=2, category=DeprecationWarning)
            return func(*args, **kwargs)

        return wrapped

    return wrapper


def attribute(recommendation):
    # type: (tp.Text) -> tp.Callable[[tp.Callable], tp.Callable]
    def wrapper(attr):
        @wraps(attr)
        def wrapped(*args, **kwargs):
            msg = "Use of {} is deprecated: {}".format(attr.__name__, recommendation)
            warnings.warn(msg, stacklevel=2, category=DeprecationWarning)
            return attr(*args, **kwargs)

        return wrapped

    return wrapper


warnings.filterwarnings("default", module="applitools")
