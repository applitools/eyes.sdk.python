from __future__ import absolute_import, unicode_literals

import os
import re
import shutil
from collections import OrderedDict
from enum import Enum
from typing import Any, Generator, Text, Type

from robot.libraries.BuiltIn import BuiltIn

from applitools.common import RectangleSize, Region
from applitools.common.utils import argument_guard
from applitools.common.validators import is_webelement
from applitools.selenium.fluent import SeleniumCheckSettings

SEPARATOR = object()


def extract_keyword_and_arguments(
    keywords_from_test,  # type: list[Any]|tuple[Any]
    defined_keywords,  # type: list[Any]|tuple[Any]
):
    # type: (...) -> Generator[tuple[Text, list[Any]], None, None]
    res = OrderedDict()
    key_keyword = None
    key_keyword_index = -1
    for i, keyword in enumerate(keywords_from_test):
        if keyword == key_keyword and key_keyword_index != i:
            # Next keyword with similar name
            res[key_keyword].append(SEPARATOR)

        if keyword in defined_keywords:
            key_keyword = keyword
            key_keyword_index = i
            if key_keyword not in res:
                res[key_keyword] = []
            continue

        if key_keyword is None:
            raise ValueError(
                "Incorrect keyword argument. Keywords: {}".format(keywords_from_test)
            )
        res[key_keyword].append(keyword)
    for keyword, arguments in res.items():
        yield keyword, arguments


def splits_args_by_separator(args):
    # type: (list[Any]) -> Generator[tuple[Any], None, None]
    res = ()
    for i, arg in enumerate(args, start=1):
        if arg is not SEPARATOR:
            res += (arg,)
        else:
            yield res
            res = ()
            continue

        if len(args) <= i:
            yield res


def collect_check_settings(check_settings, defined_keywords, *keywords):
    # type: (SeleniumCheckSettings,list[str],tuple[Any])->SeleniumCheckSettings
    """Fill `check_setting` with data from keyword and return `check_settings`"""
    for keyword, keyword_args in extract_keyword_and_arguments(
        keywords, defined_keywords
    ):
        if keyword_args:
            # keyword has arguments
            for separated_args in splits_args_by_separator(keyword_args):
                separated_args += (check_settings,)
                BuiltIn().run_keyword(keyword, *separated_args)
        else:
            # in case keyword without args like `Fully`
            BuiltIn().run_keyword(keyword, check_settings)
    return check_settings


int_float_pattern = r"\d+(?:\.\d+)?"


def parse_viewport_size(text):
    # type: (Text) -> RectangleSize
    num_ptrs = (int_float_pattern,) * 2
    match = re.match(r"\[(%s) (%s)\]" % num_ptrs, text)
    if match is None:
        raise ValueError(
            "Incorrect value of viewport: {}.\n\t Format should be: [800 700]".format(
                text
            )
        )
    groups = match.groups()
    return RectangleSize(width=float(groups[0]), height=float(groups[1]))


def parse_region(text):
    num_ptrs = (int_float_pattern,) * 4
    match = re.match(r"\[(%s) (%s) (%s) (%s)\]" % num_ptrs, text)
    if match is None:
        raise ValueError(
            "Incorrect value of region: {}.\n\t Format should be: [10 10 10 10]".format(
                text
            )
        )
    groups = match.groups()
    return Region(
        left=float(groups[0]),
        top=float(groups[1]),
        width=float(groups[2]),
        height=float(groups[3]),
    )


def is_webelement_guard(element):
    argument_guard.is_valid_type(
        is_webelement(element),
        "element argument should be type Selenium or Appium Web Element",
    )


def get_config_file_path():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(here, "applitools.yaml")


def copy_config_to(path_to_dir):
    if not os.path.exists(path_to_dir):
        raise ValueError("Directory doesn't exists")
    return shutil.copy(get_config_file_path(), path_to_dir)


def get_enum_by_name(name, enm):
    # type: (Text, Type[Enum]) -> Enum
    try:
        return getattr(enm, name)
    except AttributeError:
        raise ValueError("`{}` does not contain `{}`".format(enm, name))


def get_enum_by_upper_name(name, enm):
    # type: (Text, Type[Enum]) -> Enum
    return get_enum_by_name(name.upper(), enm)
