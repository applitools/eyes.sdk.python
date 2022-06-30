*** Settings ***
Resource    resources/setup.robot
#Library     ${BACKEND_LIBRARY_NAME}
Library     SeleniumLibrary
Library     EyesLibrary     runner=${RUNNER}

Test Setup       Setup
Test Teardown    Teardown
Suite Teardown   Eyes Get All Test Results

*** Variables ***
${FORM_XPATH}               //html/body/div/div/form
${FORM_USERNAME_XPATH}      //html/body/div/div/form/div[1]

*** Test Cases ***
Check Window
    Eyes Check Window    Ignore Region By Coordinates    [12 22 2 2]

Check Window Fully
    Eyes Check Window       Fully

Check Region By Element
    ${element}=     Get WebElement          ${FORM_XPATH}
    Eyes Check Region By Element    ${element}

Check Region By Selector
    Eyes Check Region By Selector    ${FORM_XPATH}

Check Region By Selector With Ignore
    Eyes Check Region By Selector    ${FORM_XPATH}
    ...     Ignore Region By Coordinates    [12 22 22 22]

Check Window Two Times
    Eyes Check Window       first
    Eyes Check Window       second

Check Shadow Dom
    Go To        https://applitools.github.io/demo/TestPages/ShadowDOM/index.html
    Eyes Check Region By Target Path
    ...     Shadow By Selector    css:#has-shadow-root
    ...     Region By Selector   css:h1

