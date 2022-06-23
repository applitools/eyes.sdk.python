*** Settings ***
Resource    shared_variables.robot
Library     SeleniumLibrary
Library     EyesLibrary     runner=${RUNNER}      config=../applitools.yaml

Suite Teardown    Eyes Get All Test Results

*** Test Cases ***
Check Window Suite 3
    Open Browser                              ${URL}      ${BROWSER}
    Eyes Open
    Eyes Check Window
    Eyes Close Async
    Close All Browsers

