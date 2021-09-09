*** Settings ***
Resource    shared_variables.robot
Library     SeleniumLibrary
Library     EyesLibrary     runner=${RUNNER}      config=../applitools.yaml

*** Test Cases ***
Check Window Suite 2
    Open Browser                              ${URL}      ${BROWSER}
    Eyes Open
    Eyes Check Window
    Eyes Close Async
    Close All Browsers

