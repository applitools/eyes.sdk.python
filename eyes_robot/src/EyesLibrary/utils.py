from collections import defaultdict
from typing import Any, Generator, Text

from robot.libraries.BuiltIn import BuiltIn

from applitools.selenium.fluent import SeleniumCheckSettings

SEPARATOR = object()


def extract_keyword_and_arguments(
    keywords_from_test,  # type: list[Any]|tuple[Any]
    defined_keywords,  # type: list[Any]|tuple[Any]
):
    # type: (...) -> Generator[tuple[Text, list[Any]], None, None]
    # need to reverse for return correct index with bisect
    res = defaultdict(list)
    key_keyword = None
    key_keyword_index = -1
    for i, keyword in enumerate(keywords_from_test):
        if keyword == key_keyword and key_keyword_index != i:
            # Next keyword with similar name
            res[key_keyword].append(SEPARATOR)

        if keyword in defined_keywords:
            key_keyword = keyword
            key_keyword_index = i
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


def collect_check_settings(
    check_settings, defined_keywords, *keywords, executor=BuiltIn().run_keyword
):
    # type: (SeleniumCheckSettings,list[str],tuple[Any],callable)->SeleniumCheckSettings
    """ Fill `check_setting` with data from keyword and return `check_settings`"""
    for keyword, args in extract_keyword_and_arguments(keywords, defined_keywords):
        for separated_args in splits_args_by_separator(args):
            separated_args += (check_settings,)
            executor(keyword, *separated_args)
    return check_settings
