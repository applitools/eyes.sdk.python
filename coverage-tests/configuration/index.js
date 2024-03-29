let ref = "b1e7d6b3";
module.exports = {
    name: 'eyes_selenium_python',
    emitter: `https://raw.githubusercontent.com/applitools/sdk.coverage.tests/${ref}/python/emitter.js`,
    overrides: [
        `https://raw.githubusercontent.com/applitools/sdk.coverage.tests/${ref}/js/overrides.js`,
        `https://raw.githubusercontent.com/applitools/sdk.coverage.tests/${ref}/python/overrides.js`,
    ],
    template: `https://raw.githubusercontent.com/applitools/sdk.coverage.tests/${ref}/python/template.hbs`,
    tests: `https://raw.githubusercontent.com/applitools/sdk.coverage.tests/${ref}/coverage-tests.js`,
    ext: '.py',
    outPath: './test/coverage/generic',
}
