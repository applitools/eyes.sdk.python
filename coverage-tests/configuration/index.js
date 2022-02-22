module.exports = {
    name: 'eyes_selenium_python',
    emitter: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/universal_python_update_shadow/python/emitter.js',
    overrides: [
        'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/universal-sdk/js/overrides.js',
        './configuration/python_overrides_universal'],
    template: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/master/python/template.hbs',
    tests: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/universal-sdk/coverage-tests.js',
    ext: '.py',
    outPath: './test/coverage/generic',
}
