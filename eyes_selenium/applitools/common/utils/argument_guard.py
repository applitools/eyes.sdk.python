from six import iteritems

from applitools.common.validators import is_list_or_tuple


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


def is_valid_type(is_valid, message):
    """
    Fails if is_valid is false.
    """
    if not is_valid:
        raise TypeError(message)


def is_a(param, klass, exc_info=None):
    if not isinstance(param, klass):
        if exc_info:
            raise exc_info
        raise ValueError("`{}` is not instance of `{}`".format(param, klass))


def are_(params, klass, exc_info=None):
    for param in params:
        is_a(param, klass, exc_info)
