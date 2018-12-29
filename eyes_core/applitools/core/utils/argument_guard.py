import typing as tp

from applitools.core.errors import EyesIllegalArgument
from .compat import iteritems


def get_name_from_param(param):
    for var_name, var in iteritems(locals()):
        if var is param:
            return var_name


def not_none(param):
    """
    Fails if the input parameter is None
    """
    if param is None:
        raise ValueError('{} is None'.format(get_name_from_param(param)))


def not_none_or_empty(param):
    """
    Fails if the input parameter string is null or empty.
    """
    not_none(param)
    if not param:
        raise ValueError('{} is empty'.format(get_name_from_param(param)))


def greater_than_or_equal_to_zero(param, *args):
    # type: (int, *int) -> None
    """
    Fails if the input integer parameter is negative.
    """
    if args:
        # adaptation for attr library
        param = args[1]
    if 0 >= param:
        raise ValueError('{} < 0'.format(get_name_from_param(param)))


# TODO: update after resolving issue
def greater_than_zero(param):
    # type: (int) -> None
    if 0 >= param:
        raise ValueError('{} < 1'.format(get_name_from_param(param)))


def is_valid_state(is_valid, message):
    """
    Fails if is_valid is false.
    """
    if not is_valid:
        raise Exception(message)


def is_a(param, klass):
    if not isinstance(param, klass):
        raise EyesIllegalArgument('{} is not instance of {}'.format(param, klass))
