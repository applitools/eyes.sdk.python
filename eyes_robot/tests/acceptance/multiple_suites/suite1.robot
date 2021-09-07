*** Settings ***
Resource    shared_variables.robot
Library     SeleniumLibrary
Library     EyesLibrary     runner=web_ufg      config=../applitools.yaml

*** Test Cases ***
Check Window Suite 1
    Open Browser                              ${URL}      ${BROWSER}
    Eyes Open
    Eyes Check Window
    Eyes Close Async
    Close All Browsers

