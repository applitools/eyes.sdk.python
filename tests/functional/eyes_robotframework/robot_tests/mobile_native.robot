*** Settings ***
Resource    resources/setup.robot
Library     AppiumLibrary
Library     EyesLibrary     runner=${RUNNER}

Test Setup       Setup
Test Teardown    Teardown
Suite Teardown   Eyes Get All Test Results


*** Test Cases ***
Check Window Native
    Sleep  10s
    Eyes Check Window    Ignore Region By Coordinates    [12 22 2 2]
