module.exports = {
    name: "eyes_selenium_python",
    emitter: "https://raw.githubusercontent.com/applitools/sdk.coverage.tests/master/python/emitter.js",
    overrides: [
        "https://raw.githubusercontent.com/applitools/sdk.coverage.tests/master/python/overrides.js",
        "https://raw.githubusercontent.com/applitools/sdk.coverage.tests/master/eg.overrides.js",
    ],
    template: "https://raw.githubusercontent.com/applitools/sdk.coverage.tests/master/python/template.hbs",
    ext: ".py",
    outPath: "./test/coverage/generic",
};
