import typing
import warnings
from functools import wraps
from inspect import getcallargs


def module(name, recommendation):
    # type: (typing.Text, typing.Text) -> None
    message = "Module {} is deprecated: {}".format(name, recommendation)
    warnings.warn(message, stacklevel=2, category=ImportWarning)


def argument(name, recommendation):
    # type: (typing.Text, typing.Text) -> None
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
