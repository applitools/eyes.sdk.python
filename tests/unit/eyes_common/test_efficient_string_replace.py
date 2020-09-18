import pytest

from applitools.common.utils.efficient_string_replace import (
    clean_for_json,
    efficient_string_replace,
)


def test_efficient_string_replace():
    res = efficient_string_replace(
        "@<",
        ">#",
        "abcdef@<0>#ghijklmnop@<1>#qrstuv@<2>#wx@<1>#@<0>#yz",
        {"0": "ABCDEFG", "1": "HIJKLMNOP", "2": "QRSTUV", "3": "WXYZ"},
    )
    assert res == "abcdefABCDEFGghijklmnopHIJKLMNOPqrstuvQRSTUVwxHIJKLMNOPABCDEFGyz"


def test_efficient_string_replace_recursive_forward():
    res = efficient_string_replace(
        "@<", ">#", "abc@<0>#ghi@<1>#mno@<2>#", {"0": "@<1>#", "1": "JKL", "2": "PQR"},
    )
    assert res == "abcJKLghiJKLmnoPQR"


def test_efficient_string_replace_recursive_backward():
    res = efficient_string_replace(
        "@<", ">#", "abc@<0>#ghi@<1>#mno@<2>#", {"0": "DEF", "1": "@<0>#", "2": "PQR"},
    )
    assert res == "abcDEFghiDEFmnoPQR"


def test_efficient_string_replace_recursive_loop_raises():
    with pytest.raises(RuntimeError, match="Cyclic replacement pattern found"):
        res = efficient_string_replace(
            "@<",
            ">#",
            "abc@<0>#ghi@<1>#mno@<2>#",
            {"0": "@<1>#", "1": "@<0>#", "2": "PQR"},
        )
        assert res == "abcDEFghiDEFmnoPQR"


def test_clean_for_json():
    assert clean_for_json("\b\t\n\f\r") == r"\b\t\n\f\r"
    assert clean_for_json('"/') == r"\"/"
    assert clean_for_json("\\") == r"\\"
    assert clean_for_json(chr(25)) == r"\u0019"
