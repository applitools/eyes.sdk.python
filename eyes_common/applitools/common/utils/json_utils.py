import enum
import json
import re
from datetime import datetime

import attr

from applitools.common.utils import iteritems


def to_json(val):
    return json.dumps(val, default=to_serializable, sort_keys=True)


def _fields_from_attr(cls):
    return [field.name for field in attr.fields(cls)]


def _klasses_from_attr(cls):
    klasses = {}
    klasses[cls] = _fields_from_attr(cls)
    for field in attr.fields(cls):
        if field.type and attr.has(field.type):
            klasses[field.type] = _fields_from_attr(field.type)
    return klasses


def attr_from_json(content, cls):
    klasses = _klasses_from_attr(cls)

    def make_snake(dct):
        params = {}
        for k, v in iteritems(dct):
            k = camelcase_to_underscore(k)
            # if k in fields:
            params[k] = v
        return params

    def obj_came(obj):
        params = make_snake(dict(obj))
        for kls, fields in iteritems(klasses):
            if len(klasses) == 1:
                cleaned_params = {
                    key: val for key, val in iteritems(params) if key in fields
                }
                return kls(**cleaned_params)

            coincidence = 0
            for key in params.keys():
                if key in fields:
                    coincidence += 1
            if coincidence >= 2:
                cleaned_params = {
                    key: val for key, val in iteritems(params) if key in fields
                }
                return kls(**cleaned_params)

    instance = json.loads(content, object_hook=obj_came)
    return instance


def attr_from_response(response, cls):
    return attr_from_json(response.text, cls)


class _CamelCasedDict(dict):
    def __setitem__(self, key, value):
        key = underscore_to_camelcase(key)
        if hasattr(value, "value"):
            value = value.value
        super(_CamelCasedDict, self).__setitem__(key, value)


def _filter(attr_, value):
    if attr_.name.startswith("_"):
        return False
    if attr_.metadata.get(JsonInclude.NON_NONE):
        if value is None:
            return False
        return True
    if attr_.metadata.get(JsonInclude.THIS) or attr_.metadata.get(JsonInclude.NAME):
        return True
    return False


def to_serializable(val):
    if isinstance(val, datetime):
        return val.isoformat() + "Z"
    elif isinstance(val, enum.Enum):
        return val.value
    elif attr.has(val.__class__):
        name = getattr(val, "JSON_NAME", None)
        obj = attr.asdict(val, filter=_filter, dict_factory=_CamelCasedDict)
        if name:
            return {name: obj}
        return obj
    elif isinstance(val, bytes):
        return val
    elif isinstance(val, Exception):
        return {"error": val.__class__.__name__, "args": val.args}
    return str(val)


def camelcase_to_underscore(text):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def underscore_to_camelcase(text):
    return re.sub(r"(?!^)_([a-zA-Z])", lambda m: m.group(1).upper(), text)


class JsonInclude(object):
    NON_NONE = "non_none"
    THIS = "include"
    NAME = "name"
