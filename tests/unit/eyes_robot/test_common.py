from EyesLibrary.utils import (
    SEPARATOR,
    extract_keyword_and_arguments,
    splits_args_by_separator,
)


def test_extract_keyword_and_arguments(defined_keywords):
    keywords_from_test = [
        "Ignore Region By Element",
        "WebElement",
        "Ignore Region By Coordinates",
        40,
        24,
        24,
        56,
    ]
    result = list(extract_keyword_and_arguments(keywords_from_test, defined_keywords))
    assert result[0] == ("Ignore Region", ["WebElement"])
    assert result[1] == ("Ignore Region By Coordinates", [40, 24, 24, 56])


def test_extract_keyword_and_arguments_with_similar_keyword(defined_keywords):
    keywords_from_test = [
        "Ignore Region",
        "WebElement",
        "Ignore Region",
        "WebElement",
        "Ignore Region By Coordinates",
        40,
        24,
        24,
        56,
    ]
    result = list(extract_keyword_and_arguments(keywords_from_test, defined_keywords))
    assert result[0] == ("Ignore Region", ["WebElement", SEPARATOR, "WebElement"])
    assert result[1] == ("Ignore Region By Coordinates", [40, 24, 24, 56])


def test_splits_args_by_separator(defined_keywords):
    result = list(splits_args_by_separator(["WebElement"]))
    assert result[0] == ("WebElement",)

    result = list(splits_args_by_separator(["WebElement", SEPARATOR, "WebElement"]))
    assert result[0] == ("WebElement",)
    assert result[1] == ("WebElement",)

    result = list(
        splits_args_by_separator(
            ["WebElement", SEPARATOR, "WebElement", SEPARATOR, 0, 3, 2, 1]
        )
    )
    assert result[0] == ("WebElement",)
    assert result[1] == ("WebElement",)
    assert result[2] == (0, 3, 2, 1)
