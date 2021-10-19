STATE = {"dont_close_batches": {"type": bool, "value": False}}


def set(name, value):
    try:
        value_obj = STATE[name]
    except KeyError:
        raise KeyError("name `{}` is not in state".format(name))
    if not isinstance(value, value_obj["type"]):
        raise TypeError("value type isn't supported")
    value_obj["value"] = value


def get(name):
    try:
        value_obj = STATE[name]
    except KeyError:
        raise KeyError("name `{}` is not in state".format(name))
    return value_obj["value"]
