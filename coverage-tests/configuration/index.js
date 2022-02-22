module.exports = {
    name: 'eyes_selenium_python',
    emitter: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/mobile-web-python/python/emitter.js',
    overrides: [
        'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/mobile-web-python/js/overrides.js',
        './configuration/python_overrides_universal'],
    template: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/mobile-web-python/python/template.hbs',
    tests: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/mobile-web-python/coverage-tests.js',
    ext: '.py',
    outPath: './test/coverage/generic',
}
