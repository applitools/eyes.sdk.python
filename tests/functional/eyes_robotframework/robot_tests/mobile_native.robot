*** Settings ***
Resource    resources/setup.robot
Library     AppiumLibrary
Library     EyesLibrary     runner=mobile_native

Test Setup       Setup
Test Teardown    Teardown
Suite Teardown   Eyes Get All Test Results


*** Test Cases ***
Check Window
    Eyes Check Window    Ignore Region By Coordinates    [12 22 2 2]
