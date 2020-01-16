import enum
import json
import re
from collections import defaultdict, Counter
from datetime import datetime
from typing import Dict, Text

import attr

from applitools.common import logger

from .compat import iteritems


def to_json(val):
    return json.dumps(val, default=to_serializable, sort_keys=True)


def _fields_from_attr(cls):
    return [
        field.name
        for field in attr.fields(cls)
        if JsonInclude.THIS in field.metadata.keys()
    ]


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
        def cleaned_params(params, fields):
            return {key: val for key, val in iteritems(params) if key in fields}

        params = make_snake(dict(obj))
        convidenced = defaultdict(int)
        for kls, fields in iteritems(klasses):
            fields = tuple(fields)
            if len(klasses) == 1:
                return kls(**cleaned_params(params, fields))
            if set(params.keys()) == set(fields):
                return kls(**cleaned_params(params, fields))

            for key in params.keys():
                if key in fields:
                    convidenced[(kls, fields)] += 1
        try:
            (kls, fields), _ = Counter(convidenced).most_common()[0]
            return kls(**cleaned_params(params, fields))
        except IndexError:
            # Failed to convert any class. Use raw object instead
            return params

    instance = json.loads(content, object_hook=obj_came)
    return instance


def attr_from_response(response, cls):
    return attr_from_json(response.text, cls)


# Uses for replacing of regular attr.name to specified in metadata
REPLACE_TO_DICT = dict()  # type: Dict[Text, Text]


class _CamelCasedDict(dict):
    def __setitem__(self, key, value):
        if key in REPLACE_TO_DICT:
            # use key specified in metadata
            old_key = key
            key = REPLACE_TO_DICT[old_key]
            del REPLACE_TO_DICT[old_key]
        else:
            # convert key into camel case format
            key = underscore_to_camelcase(key)
        # process Enum's
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
    if attr_.metadata.get(JsonInclude.THIS):
        return True
    if attr_.metadata.get(JsonInclude.NAME):
        # set key from metadata which would be used by default
        REPLACE_TO_DICT[attr_.name] = attr_.metadata[JsonInclude.NAME]
        return True
    return False


def to_serializable(val):
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%dT%H:%M:%SZ")
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
