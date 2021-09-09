*** Settings ***
Resource    resources/setup.robot
Library     ${BACKEND_LIBRARY_NAME}
Library     EyesLibrary     runner=${RUNNER}

Test Setup       Setup
Test Teardown    Teardown
Suite Teardown   Eyes Get All Test Results


*** Test Cases ***
Check Window
    Eyes Check Window    Ignore Region By Coordinates    [12 22 2 2]


Check Window Fully
    Eyes Check Window       Fully


Eyes Open Close Multiple Times
    Eyes Check Window       Fully


Check Region By Element
    ${element}=     Get WebElement          overflowing-div
    Eyes Check Region By Element    ${element}

Check Region By Selector
    Eyes Check Region By Selector    overflowing-div

Check Region By Selector With Ignore
    Eyes Check Region By Selector    overflowing-div
    ...     Ignore Region By Coordinates    [12 22 22 22]

Check Window Two Times
    Eyes Check Window       first
    Eyes Check Window       second

Check Region By Coordinates In Frame
    Eyes Check Region By Coordinates    [30 40 400 1200]        [name="frame1"]
