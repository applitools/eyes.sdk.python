import typing
import warnings


def module(name, recommendation):
    # type: (typing.Text, typing.Text) -> None
    message = "Module {} is deprecated: {}".format(name, recommendation)
    warnings.warn(message, stacklevel=2, category=ImportWarning)
