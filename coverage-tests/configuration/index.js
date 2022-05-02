module.exports = {
    name: 'eyes_selenium_python',
    emitter: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/fix_wait_before_capture_test/python/emitter.js',
    overrides: [
        'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/universal-sdk/js/overrides.js',
        'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/universal-sdk/python/overrides.js',
    ],
    template: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/universal-sdk/python/template.hbs',
    tests: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/fix_wait_before_capture_test/coverage-tests.js',
    ext: '.py',
    outPath: './test/coverage/generic',
}
