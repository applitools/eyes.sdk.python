*** Variables ***
${URL}                          https://demo.applitools.com/
${BROWSER_NAME}                 Chrome

*** Keywords ***
Setup
    Set Eyes Configure Property     RUNNER    ${RUNNER}
    Set Eyes Configure Property     BACKEND_LIBRARY_NAME    ${RUNNER}
    IF  '${BACKEND_LIBRARY_NAME}' == 'AppiumLibrary'
        Open Application        ${REMOTE_URL}    &{DESIRED_CAPS}
        IF  '${RUNNER}' == 'web'
            Go To Url   ${URL}
        END
        Eyes Open   batch=${BATCH_NAME}
    ELSE IF  '${BACKEND_LIBRARY_NAME}' == 'SeleniumLibrary'
        Open Browser   ${URL}   ${BROWSER_NAME}   remote_url=${REMOTE_URL}   desired_capabilities=${DESIRED CAPS}
        Eyes Open   batch=${BATCH_NAME}  viewport_size=[989 637]
    END


Teardown
    IF  '${BACKEND_LIBRARY_NAME}' == 'AppiumLibrary'
        Close Application
    ELSE IF  '${BACKEND_LIBRARY_NAME}' == 'SeleniumLibrary'
        Close All Browsers
    END
    Eyes Close Async
