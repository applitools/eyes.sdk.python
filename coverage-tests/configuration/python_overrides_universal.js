module.exports = {
    // fails in selenium4 only due to legacy driver being used
    'check window after manual scroll on safari 11': {skip: true},

    // Shadow emitter not implemented
    'check region by element within shadow dom with vg': {skip: true},

    // Stale element are not handled by python binding
    'should handle check of stale element if selector is preserved': {skip: true},
    'should handle check of stale element in frame if selector is preserved': {skip: true},

    // Failing on the universal server 1.10 and lower
    // check on new universal server version
    "check window on mobile web android": {skip: true},

    // Temporarily disabled until generation fixed
    'should abort after close with vg': {skipEmit: true},
	'should abort unclosed tests': {skipEmit: true},
    'should abort unclosed tests with vg': {skipEmit: true},
    'should return aborted tests in getAllTestResults': {skipEmit: true},
    'should return aborted tests in getAllTestResults with vg': {skipEmit: true},
    'should return browserInfo in getAllTestResults': {skipEmit: true},
    'appium iOS check window region with scroll and pageCoverage': {skip: true},
    'should send agentRunId': {skip: true},
    'should waitBeforeCapture in open': {skip: true},
    'should waitBeforeCapture in check': {skip: true},
}
