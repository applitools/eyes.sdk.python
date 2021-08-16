*** Settings ***
Library     SeleniumLibrary
Library     EyesLibrary     runner=selenium    log_level=VERBOSE    config=resources/applitools_config.yaml
Library     robot

*** Variables ***
&{LOGO}     id=hplogo                 xpath=//*[@id="hplogo"]
${BROWSER}        Chrome
${URL}      https://applitools.com/helloworld/


*** Test Cases ***
Docs
    ${robot.libdoc.libdoc()}
