const local = {
    name: 'eyes_selenium_python',
    emitter: '../../sdk.coverage.tests/python/emitter.js',
    overrides: '../../sdk.coverage.tests/python/overrides.js',
    template: '../../sdk.coverage.tests/python/template.hbs',
    tests: '../../sdk.coverage.tests/coverage-tests.js',
    ext: '.py',
    outPath: './test/coverage/generic',
}

const main = {
    name: 'eyes_selenium_python',
    emitter: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/master/python/emitter.js',
    overrides: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/master/python/overrides.js',
    template: 'https://raw.githubusercontent.com/applitools/sdk.coverage.tests/master/python/template.hbs',
    ext: '.py',
    outPath: './test/coverage/generic',
    emitOnly: ['/should send region by selector in padded page/']
}

module.exports = main
