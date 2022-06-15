module.exports = {
    name: 'eyes_selenium_python',
    emitter: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/d5e3833f2fac/python/emitter.js',
    overrides: [
        'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/d5e3833f2fac/js/overrides.js',
        'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/d5e3833f2fac/python/overrides.js',
    ],
    template: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/d5e3833f2fac/python/template.hbs',
    tests: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/d5e3833f2fac/coverage-tests.js',
    ext: '.py',
    outPath: './test/coverage/generic',
}
