from os.path import join

import mock
import pytest

from EyesLibrary import EyesLibrary, SelectedRunner
from EyesLibrary.utils import copy_config_to


def get_variable_value(path):
    copy_config_to(path)

    def func(name, *args):
        if name == "${SUITE_SOURCE}":
            return path

    return func


def get_library_instance(name):
    libs = {"SeleniumLibrary": mock.Mock(), "AppiumLibrary": mock.Mock()}
    return libs.get(name)


def test_use_config_from_test_folder_if_no_config_path(tmp_path):
    with mock.patch(
        "robot.libraries.BuiltIn.BuiltIn.get_variable_value",
        side_effect=get_variable_value(tmp_path),
    ), mock.patch(
        "robot.libraries.BuiltIn.BuiltIn.get_library_instance",
        side_effect=get_library_instance,
    ):
        lib = EyesLibrary()
    assert lib.selected_runner == SelectedRunner.web
    assert lib.configure


def test_pasrse_config_from_relative_folder(tmp_path):
    assert False


def test_pasrse_config_from_absolute_folder(tmp_path):
    with mock.patch(
        "robot.libraries.BuiltIn.BuiltIn.get_variable_value",
        side_effect=get_variable_value(tmp_path),
    ), mock.patch(
        "robot.libraries.BuiltIn.BuiltIn.get_library_instance",
        side_effect=get_library_instance,
    ):
        lib = EyesLibrary()
    assert lib.selected_runner == SelectedRunner.web
    assert lib.configure
