from applitools.common.validators import is_list_or_tuple

from .compat import iteritems


def get_name_from_param(param):
    for var_name, var in iteritems(locals()):
        if var is param:
            return var_name


def not_none(param, exc_info=None):
    """
    Fails if the input parameter is None
    """
    if param is None:
        if exc_info:
            raise exc_info
        raise ValueError("{} is None".format(get_name_from_param(param)))


def not_list_or_tuple(param, exc_info=None):
    """
    Fails if param is not a list or tuple
    """
    if not is_list_or_tuple(param):
        if exc_info:
            raise exc_info
        raise ValueError("{} is not list or tuple".format(get_name_from_param(param)))


def not_none_or_empty(param, exc_info=None):
    """
    Fails if the input parameter string is null or empty.
    """
    not_none(param)
    if not param:
        if exc_info:
            raise exc_info
        raise ValueError("{} is empty".format(get_name_from_param(param)))


def greater_than_or_equal_to_zero(param, *args):
    # type: (int, *int, Exception) -> None
    """
    Fails if the input integer parameter is negative.
    """
    if args:
        # adaptation for attr library
        param = args[1]
    if 0 >= param:
        raise ValueError("{} < 0".format(get_name_from_param(param)))


# TODO: update after resolving issue
def greater_than_zero(param, exc_info=None):
    # type: (int) -> None
    if 0 >= param:
        if exc_info:
            raise exc_info
        raise ValueError("{} < 1".format(get_name_from_param(param)))


def is_valid_state(is_valid, message):
    """
    Fails if is_valid is false.
    """
    if not is_valid:
        raise ValueError(message)


def is_a(param, klass, exc_info=None):
    if not isinstance(param, klass):
        if exc_info:
            raise exc_info
        raise ValueError("{} is not instance of {}".format(param, klass))


def is_in(param, klass, exc_info=None):
    if not any(isinstance(param, kls) for kls in klass):
        if exc_info:
            raise exc_info
        raise ValueError("{} is not instance of {}".format(param, klass))


def are_(params, klass, exc_info=None):
    for param in params:
        is_a(param, klass, exc_info)
