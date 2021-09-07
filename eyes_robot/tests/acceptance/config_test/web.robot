*** Settings ***
Library     SeleniumLibrary
Library     EyesLibrary

Test Setup    Setup
Test Teardown    Teardown

*** Variables ***
&{LOGO}     id=hplogo                 xpath=//*[@id="hplogo"]
${BROWSER}        Chrome
${URL}      https://applitools.github.io/demo/TestPages/FramesTestPage/

*** Keywords ***
Setup
    Open Browser                              ${URL}      ${BROWSER}

Teardown
    Close All Browsers


*** Test Cases ***
Check Window
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Window    Ignore Region By Coordinates    [12 22 2 2]
    Eyes Close Async

Check Window Fully
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Window       Fully
    Eyes Close Async


Eyes Open Close Multiple Times
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Window       Fully
    Eyes Abort Async


Check Region By Element
    Eyes Open   Eyes Selenium SDK - Classic API
    ${element}=     Get WebElement          id:overflowing-div
    Eyes Check Region By Element    ${element}
    Eyes Close Async

Check Region By Selector
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Region By Selector    id:overflowing-div
    Eyes Close Async

Check Region By Selector With Ignore
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Region By Selector    id:overflowing-div
    ...     Ignore Region By Coordinates    [12 22 22 22]
    Eyes Close Async

Check Window Two Times
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Window       first
    Eyes Check Window       second
    Eyes Close Async

Check Region By Coordinates In Frame
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Region By Coordinates    [30 40 400 1200]        [name="frame1"]
    Eyes Close Async

#Check Frame In Frame Fully
#    Eyes Open   Eyes Selenium SDK - Fluent API
#    Eyes Check  Target Frame By Name    frame1      Target Frame By Name    frame1-1    Fully
#    Eyes Close Async
#