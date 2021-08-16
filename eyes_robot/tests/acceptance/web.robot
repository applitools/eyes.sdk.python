*** Settings ***
Resource    resources/config_eyes.robot
Library     SeleniumLibrary
Library     EyesLibrary     runner=${RUNNER}    log_level=${LOG_LEVEL}    config=${CONFIG}
Test Setup    Setup
Test Teardown    Teardown

*** Variables ***
&{LOGO}     id=hplogo                 xpath=//*[@id="hplogo"]
${BROWSER}        Chrome
${URL}      https://applitools.github.io/demo/TestPages/FramesTestPage/

*** Keywords ***
Setup
    Open Browser                              ${URL}      ${BROWSER}
    Eyes Open   app_name=Overwrite app name from config      viewport_size=[800 600]

Teardown
    Close All Browsers
    Eyes Close


*** Test Cases ***
Check Window
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Window
    Eyes Close

Check Window Fully
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Window       Fully
    Eyes Close

Check Window Two Times
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Window       first
    Eyes Check Window       second
    Eyes Close

Check Region By Coordinates In Frame
    Eyes Open   Eyes Selenium SDK - Classic API
    Eyes Check Region By Coordinates    [30 40 400 1200]        [name="frame1"]
    Eyes Close

Check Frame In Frame Fully
    Eyes Open   Eyes Selenium SDK - Fluent API
    Eyes Check  Target Frame By Name    frame1      Target Frame By Name    frame1-1    Fully
    Eyes Close


Check Region By Selector
    Eyes Check Region By Selector   css:                     Google Homepage

Check Exctracted Target
    Open Browser                              ${URL}      ${BROWSER}
    ${target}=    Target Window
    ...     Ignore Region        //div[@class='demo-page center']
    Eyes Open
    Eyes Check      ${target}
    Eyes Close

Check Window and Region With Fluent
    Open Browser                              ${URL}      ${BROWSER}
    Eyes Open
    Eyes Check Window   First check
    ...     Ignore Region       //div[@class='demo-page center']
    Eyes Check Region   Second check     //div[@class='demo-page center']
    Eyes Close

Check Window With Fluent Parameters
    Open Browser                              ${URL}      ${BROWSER}
    Eyes Open
    Eyes Check  Eyes Target Window
    ...     Ignore Region By Selector    xpath://div
    ...     Ignore Region By Coordinates
    ...     Match Level    STICT
    ...     Content Region
    Eyes Check Region   Second check     //div[@class='demo-page center']
    Eyes Close

Check Fluent 2
    Open Browser                              ${URL}      ${BROWSER}
    ${link}=    Get WebElement      //div[@class='demo-page center']
#    ${ignore_list}=     Create List     //div[@class='demo-page center']    ${link}
#    ${ignore_list}= Eyes Ignore     //div[@class='demo-page center']    ${link}
    ${target}=    Eyes Target Window      ignore=${ignore_list}     send_dom=True
    ${target}=    Eyes Target Region      ${link}
    Eyes Open
    Eyes Check      target
    Eyes Close


Check Fluent 3
    Open Browser                              ${URL}      ${BROWSER}
    ${link}=    Get WebElement      //div[@class='demo-page center']
#    ${ignore_list}= Eyes Ignore     //div[@class='demo-page center']    ${link}
#    ${target}=    Ignore Region By Element      ${link}
#    ${settings}=    Ignore Region By Coordinates      40  24  24  56
#    ${target}=    Check Settings      ignore=${ignore_list}     send_dom=True
#    ${target}=    Eyes Target Region      ${link}
#    Eyes Config
#    ...     Set Batch
    Eyes Open
#    Eyes Check      Eyes Target Region      ${link}
#    Eyes Check Window   Some tag
#    Eyes Check      Eyes Target Window
#    ...     Ignore Region By Element      ${link}
#    ...     Ignore Region By Coordinates      40  24  24  56
#    Eyes Check   Some tag
#    Eyes Check      Eyes Target Window
#    ...     Ignore Region By Element      ${link}
#    ...     Ignore Region By Coordinates      40  24  24  56

    ${ignore_list}=     Create List     //div[@class='demo-page center']    ${link}
#    Eyes Check Window    Some
#    ...     Ignore Region       //div[@class='section']

#    Eyes Check   Eyes Target Window       ignore=${ignore_list}    match_level="LAYOUT"
#    ${target}=  Eyes Target Window
##    ...     Ignore Region       //div[@class='section']
#    ...     Ignore Region       ${link}
#    ...     Match Level     LAYOUT

    Eyes Check   Eyes Target Window
#    ...     Ignore Region       //div[@class='section']
#    ...     Ignore Region By Coordinates    12      234     324     121
#    ...     Ignore Region       ${link}
    ...     Ignore Region      ${ignore_list}
    ...     Match Level     LAYOUT
#    ...     Ignore Region By Coordinates    34  34  43  34
    Eyes Close
