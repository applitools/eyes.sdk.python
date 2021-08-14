module.exports = {
    name: "eyes_selenium_python",
    emitter: "https://raw.githubusercontent.com/applitools/sdk.coverage.tests/eg_python/python/emitter.js",
    overrides: [
        "https://raw.githubusercontent.com/applitools/sdk.coverage.tests/eg_python/python/overrides.js",
        "https://raw.githubusercontent.com/applitools/sdk.coverage.tests/eg_python/eg.overrides.js",
    ],
    template: "https://raw.githubusercontent.com/applitools/sdk.coverage.tests/eg_python/python/template.hbs",
    ext: ".py",
    outPath: "./test/coverage/generic",
};
