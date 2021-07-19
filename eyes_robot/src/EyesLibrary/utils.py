from collections import defaultdict
from typing import Any, Generator, Text

from robot.libraries.BuiltIn import BuiltIn

from applitools.selenium.fluent import SeleniumCheckSettings


def extract_keyword_and_arguments(
    keywords_from_test,  # type: list[Any]|tuple[Any]
    defined_keywords,  # type: list[Any]|tuple[Any]
):
    # type: (...) -> Generator[tuple[Text, list[Any]], None, None]
    # need to reverse for return correct index with bisect
    res = defaultdict(list)
    key_keyword = None
    for i, keyword in enumerate(keywords_from_test):
        if keyword in defined_keywords:
            key_keyword = keyword
            continue
        if key_keyword is None:
            raise ValueError(
                "Incorrect keyword argument. Keywords: {}".format(keywords_from_test)
            )
        res[key_keyword].append(keyword)
    for keyword, arguments in res.items():
        yield keyword, arguments


def collect_check_settings(check_settings, defined_keywords, *keywords):
    # type: (SeleniumCheckSettings, list[str], tuple[Any]) -> SeleniumCheckSettings
    """ Fill `check_setting` with data from keyword and return `check_settings`"""
    for keyword, args in extract_keyword_and_arguments(keywords, defined_keywords):
        args += [check_settings]
        BuiltIn().run_keyword(keyword, *args)
    return check_settings
