module.exports = {
    name: 'eyes_selenium_python',
    emitter: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/universal-sdk/python/emitter.js',
    overrides: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/universal-sdk/js/overrides.js',
    template: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/master/python/template.hbs',
    tests: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/universal-sdk/coverage-tests.js',
    ext: '.py',
    outPath: './test/coverage/generic',
}
