import json
import re
from collections import Counter, defaultdict
from typing import TYPE_CHECKING

import attr
from six import iteritems

if TYPE_CHECKING:
    from typing import Any, Dict, Generator, Optional, Text, Tuple, Type


def _fields_name_from_attr(cls):
    # type: (Type) -> Generator[Tuple[Text, Optional[Text]]]
    if not attr.has(cls):
        raise TypeError("Class should be attrs based")
    for field in attr.fields(cls):
        if JsonInclude.THIS in field.metadata:
            yield field.name, None
        elif JsonInclude.NAME in field.metadata:
            yield field.name, camelcase_to_underscore(
                field.metadata.get(JsonInclude.NAME)
            )


def _types_and_fields_from_attr(cls):
    # type: (Type) -> Dict[Type, Any]
    types = {cls: tuple(_fields_name_from_attr(cls))}

    def traverse(cls):
        for field in attr.fields(cls):
            if field.type and attr.has(field.type):
                types[field.type] = tuple(_fields_name_from_attr(field.type))
                traverse(field.type)

    traverse(cls)
    return types


def _make_keys_as_underscore(dct):
    # type: (Dict[Text, Any]) -> Dict[Text, Any]
    params = {}
    for k, v in iteritems(dct):
        k = camelcase_to_underscore(k)
        params[k] = v
    return params


def _server_fields_name(fields):
    # type: (Tuple[Text, Optional[Text]]) -> Generator[Text]
    for loc_f, ser_f in fields:
        if ser_f:
            yield ser_f
            continue
        yield loc_f


def _cleaned_params(params, fields):
    # type: (Dict[Text, Any], Tuple[Text, Optional[Text]]) -> Dict[Text, Any]
    d = {}
    for key, val in iteritems(params):
        for loc_f, ser_f in fields:
            if key == loc_f or ser_f and key == ser_f:
                d[loc_f] = val
                break
    return d


def attr_from_json(content, cls):
    types_and_fields = _types_and_fields_from_attr(cls)

    def coincidence_find(params, coincidence, common_index=0):
        try:
            (kls, fields), _ = Counter(coincidence).most_common()[common_index]
            return kls(**_cleaned_params(params, fields))
        except TypeError:
            # in case of Region and AccessibilityRegion there could be situation when
            return coincidence_find(params, coincidence, common_index=common_index + 1)
        except IndexError:
            # Failed to convert any class. Use raw object instead
            return params

    def obj_came(obj):
        params = _make_keys_as_underscore(dict(obj))
        coincidence = defaultdict(int)
        for kls, fields in iteritems(types_and_fields):
            fields_to_compare = tuple(_server_fields_name(fields))
            if len(types_and_fields) == 1:
                return kls(**_cleaned_params(params, fields))
            if set(params.keys()) == set(fields_to_compare):
                return kls(**_cleaned_params(params, fields))

            for key in params.keys():
                if key in fields_to_compare:
                    coincidence[(kls, fields)] += 1
        return coincidence_find(params, coincidence)

    instance = json.loads(content, object_hook=obj_came)
    return instance


def camelcase_to_underscore(text):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def underscore_to_camelcase(text):
    return re.sub(r"(?!^)_([a-zA-Z])", lambda m: m.group(1).upper(), text)


class JsonInclude(object):
    NON_NONE = "non_none"
    THIS = "include"
    NAME = "name"
