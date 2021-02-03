'use strict'
const {checkSettingsParser, python, framesClassic, parseSelector, parseSelectorByType, regionParameter} = require('./parser')
const {capitalizeFirstLetter} = require('./util')

function directString(String) {
    return {
        isRef: true,
        ref: () => {
	if ((String !== undefined) && (((typeof String) === 'string') || (JSON.stringify(String).includes('true')) || (JSON.stringify(String).includes('false')))) {		
		if (String.includes('true')) String = String.replace('true','True')
		if (String.includes('false')) String = String.replace('false','False')
	}
	return String
	}
    }
}

module.exports = function (tracker, test) {
    const {addSyntax, addCommand, addHook, withScope, addType} = tracker

    function findElementFunc(element) {
    if(element.isRef) return element
    else return driver.findElement(element)
  }
   
    let mobile = ("features" in test) && (test.features[0] === 'native-selectors') ? true: false
    let emulator = ((("env" in test) && ("device" in test.env))&& !("features" in test))
    let otherBrowser = ("env" in test) && ("browser" in test.env) && (test.env.browser !== 'chrome')? true: false
    let openPerformed = false

    addType('JsonNode', {
         getter: ({target, key}) => {if (`${key}` !== "len") return `${target}[${key}]`
					else return `${key}(${target})`},
               schema: {
               attributes: { type: 'JsonNode', schema: 'JsonNode' },
               length: {type: 'Number', rename: 'len', getter: ({target, key}) => `${key}(${target})`}
               }
       })


    addHook('deps', `import pytest`)
    addHook('deps', `import selenium`)
    addHook('deps', `from selenium import webdriver`)
    addHook('deps', `from selenium.webdriver.common.by import By`)
    addHook('deps', `from selenium.webdriver.common.action_chains import ActionChains`)
    if (mobile) {
	addHook('deps', `from appium.webdriver.common.mobileby import MobileBy`)
	addHook('deps', `from applitools.core import Feature`)
    }
    addHook('deps', `from test import *`)
    addHook('deps', `from applitools.selenium import (Region, BrowserType, Configuration, Eyes, Target, VisualGridRunner, ClassicRunner, TestResults, AccessibilitySettings, AccessibilityLevel, AccessibilityGuidelinesVersion, AccessibilityRegionType)`)
    addHook('deps', `from applitools.common import StitchMode, MatchLevel`)

    addSyntax('var', ({name, value}) => `${name} = ${value}`)
    addSyntax('getter', ({target, key, type}) => {
	if (key.startsWith('get')) return `${target}.${key.slice(3).toLowerCase()}`
	if ((type !== undefined) && (type !== null) && (type.name === 'JsonNode')) return `${target}[${key}]`
	if (((type !== undefined) && (type !== null) && (type.name === 'Array')) || (Number(key))) return `${target}[${key}]`
	else return `${target}["${key}"]`
    })
    addSyntax('call', ({target, args}) => args.length > 0 ? `${target}(${args.map(val => JSON.stringify(val)).join(", ")})` : `${target}`)
    addSyntax('return', ({value}) => `return ${value}`)

    if (mobile)
    {
        let device = (test.env.device == "Samsung Galaxy S8")? "Samsung Galaxy S8 FHD GoogleAPI Emulator": test.env.device         
        addHook('beforeEach', python`@pytest.fixture(scope="function")
def dev():
    return ${device}
        `)
        addHook('beforeEach', python`@pytest.fixture(scope="function")
def app():
    return ${test.env.app}
        `)
        addHook('beforeEach', python`@pytest.fixture(scope="function")`)
        let desired_caps = (test.config.baselineName.includes("iOS"))? 'ios_desired_capabilities': 'android_desired_capabilities'
        addHook('beforeEach', python`def desired_caps(` + desired_caps + `, request, dev, app):`)
        addHook('beforeEach', python`    return ` + desired_caps)
        addHook('beforeEach', python`\n`)
    }
    else{
	    addHook('beforeEach', python`@pytest.fixture(scope="function")`)
	    addHook('beforeEach', python`def eyes_runner_class():`)
	    if (test.vg) addHook('beforeEach', python`    return VisualGridRunner(10)`)
	    else addHook('beforeEach', python`    return ClassicRunner()`)
	    addHook('beforeEach', python`\n`)

	    if (test.config.stitchMode) {
		addHook('beforeEach', python`@pytest.fixture(scope="function")`)
		addHook('beforeEach', python`def stitch_mode():`)
		if (test.config.stitchMode === 'CSS') addHook('beforeEach', python`    return StitchMode.CSS`)
		else addHook('beforeEach', python`    return StitchMode.Scroll`)
		addHook('beforeEach', python`\n`)
	    }
    }
    addHook('beforeEach', python`@pytest.fixture(scope="function")`)
    addHook('beforeEach', python`def configuration(eyes):`)
    addHook('beforeEach', python`    conf = eyes.get_configuration()`)
    addHook('beforeEach', python`    conf.test_name = ${test.config.baselineName}`)
    if ("branchName" in test.config) addHook('beforeEach', python`    conf.branch_name = ${test.config.branchName};`)
    if ("parentBranchName" in test.config) addHook('beforeEach', python`    conf.parent_branch_name = ${test.config.parentBranchName};`)
    if ("hideScrollbars" in test.config) addHook('beforeEach', python`    conf.hide_scrollbars = ${test.config.hideScrollbars};`)
    if (("defaultMatchSettings" in test.config) && ("accessibilitySettings" in test.config.defaultMatchSettings)){
	let level = `${test.config.defaultMatchSettings.accessibilitySettings.level}`
	let version = `${test.config.defaultMatchSettings.accessibilitySettings.guidelinesVersion}`
	addHook('beforeEach', python`    conf.set_accessibility_validation(AccessibilitySettings(AccessibilityLevel.` + level +`, AccessibilityGuidelinesVersion.` + version + `))`)
    }
    addHook('beforeEach', python`    return conf`)
    addHook('beforeEach', python`\n`)

    if (mobile) setUpMobileNative(test, addHook)
    else {
	if (emulator) setUpWithEmulators(test, addHook)
	else setUpBrowsers(test, addHook)
    }

    const driver = {
        constructor: {
            isStaleElementError(error) {
                addCommand(python`selenium.common.exceptions.StaleElementReferenceException`)
            },
        },
        cleanup() {
            return addCommand(python`driver.quit()`)
        },
        visit(url) {
            return addCommand(python`driver.get(${url})`)
        },
        executeScript(script, ...args) {
            if (args.length > 0) return addCommand(python`driver.execute_script(${script}, ${args[0]})`)
            return addCommand(python`driver.execute_script(${script})`)
        },
        sleep(ms) {
            console.log('Sleep was used Need to Implement')
            // TODO: implement if needed
        },
        switchToFrame(selector) {
            //return addCommand(python`driver.switch_to.frame(${selector})`)
            return addCommand(python`driver.switch_to.frame(` + framesClassic(selector) + `)`)
        },
        switchToParentFrame() {
            return addCommand(python`driver.switch_to.parent_frame()`)
        },
        findElement(selector) {
            //return addCommand(python`driver.find_element_by_css_selector(${selector})`)
            return addCommand(python`driver.find_element(` + parseSelectorByType(selector) + `)`)
        },
        findElements(selector) {
            return addCommand(python`driver.find_elements_by_css_selector(${selector})`)
        },
        getWindowLocation() {
            // return addCommand(ruby`await specs.getWindowLocation(driver)`)
            // TODO: implement if needed
        },
        setWindowLocation(location) {
            // addCommand(ruby`await specs.setWindowLocation(driver, ${location})`)
            // TODO: implement if needed
        },
        getWindowSize() {
            return addCommand(python`driver.get_window_size()`)
        },
        setWindowSize(size) {
            return addCommand(python`driver.set_window_size(${size}["width"], ${size}["height"])`)
        },
        click(element) {
            let selector = parseSelectorByType(element)
            selector = selector.replace(/\[/g, "")
	    selector = selector.replace(/\]/g, "")
            return addCommand(python`driver.find_element(` + selector + `).click()`)
        },
        type(element, keys) {
            return addCommand(python`${element}.send_keys(${keys})`)
        },
        scrollIntoView(element, align) {
            console.log('scroll into view Need to be implemented')
            return addCommand(python`driver.execute_script("arguments[0].scrollIntoView(arguments[1])", ${findElementFunc(element)}, ${align});`)
        },
        hover(element, offset) {
            console.log('hover Need to be implemented')
            return addCommand(python`hover = ActionChains(driver).move_to_element(${findElementFunc(element)})
    hover.perform()`)
        },
    }

    const eyes = {

        constructor: {
            setViewportSize(viewportSize) {
                return addCommand(python`Eyes.set_viewport_size(driver, ${viewportSize})`)
            }
        },

        getViewportSize() {
            return addCommand(python`eyes.get_viewport_size(driver)`)
        },

        runner: {
            getAllTestResults(throwEx) {
                return addCommand(python`eyes._runner.get_all_test_results(${throwEx})`)
            },
        },

        open({appName, viewportSize}) {
            let special_branch = '\n    '
            if ((`${test.config.baselineName}` === 'TestCheckOverflowingRegionByCoordinates_Fluent')
                || (`${test.config.baselineName}` === 'TestCheckOverflowingRegionByCoordinates_Fluent_Scroll')
            )
                special_branch = '\n    eyes.configure.branch_name = \"master_python\"\n    '
            let scale_mobile_app = (mobile)&&(test.name.includes('iOS')) ? 'eyes.configure.set_features(Feature.SCALE_MOBILE_APP)\n    ' : ''
            let appNm = (appName) ? appName : test.config.appName
            return addCommand(python`configuration.app_name = ${appNm}
    configuration.viewport_size = ${viewportSize}
    eyes.set_configuration(configuration)` + special_branch + scale_mobile_app +
                `eyes.open(driver)`)
        },
        check(checkSettings) {
            if(test.api === 'classic') {
		  if (checkSettings === undefined || (checkSettings.frames === undefined && checkSettings.region === undefined)) {
		    let nm = ((checkSettings) && (checkSettings.name))? checkSettings.name : undefined
                    eyes.checkWindow(nm)
		  } else if (checkSettings.frames && checkSettings.region) {
		    eyes.checkRegionInFrame(checkSettings.frames, checkSettings.region, checkSettings.timeout, checkSettings.tag, checkSettings.isFully)
		  } else if (checkSettings.frames) {
		    eyes.checkFrame(checkSettings.frames, checkSettings.timeout, checkSettings.tag)
		  } else if (checkSettings.region) {
		    eyes.checkRegion(checkSettings.region, checkSettings.tag, checkSettings.timeout, checkSettings.isFully)
		  } else {
		    throw new Error('Not implemented classic api method was tried to generate')
		  }
	      } else {
		addCommand(`eyes.check(${checkSettingsParser(checkSettings)})`)
	      }
        },
        checkWindow(tag, matchTimeout, stitchContent) {
            let Tag = !tag ? `` : `tag="${tag}"`
            let MatchTimeout = !matchTimeout ? `` : `,match_timeout=${matchTimeout}`
            let fully = !stitchContent ? `` : `, fully=${capitalizeFirstLetter(stitchContent)}`
            return addCommand(python`eyes.check_window(` + Tag + MatchTimeout + fully + `)`)
        },
        checkFrame(frameReference, matchTimeout, tag) {
            let Tag = !tag ? `` : `, tag="${tag}"`
            let MatchTimeout = !matchTimeout ? `` : `, match_timeout=${matchTimeout}`
            return addCommand(python`eyes.check_frame(` + framesClassic(frameReference) + Tag + MatchTimeout + `)`)
        },
        checkElement(element, matchTimeout, tag) {
            return addCommand(python`eyes.check(
        ${tag},
        Target.region(${element})
        .timeout(${matchTimeout})
        .fully()
      )`)
        },
        checkElementBy(selector, matchTimeout, tag) {
            return addCommand(python`eyes.check_region(
        By.CSS_SELECTOR, ${selector},
        tag=${tag},
        match_timeout=${matchTimeout},
      )`)
        },
        checkRegion(region, tag, matchTimeout, isFully) {
            /*let args = `region='${region}'` +
                `${tag ? `, tag=${tag}` : ''}` +
                `${matchTimeout ? `, timeout=${matchTimeout}` : ''}`
            return addCommand(python`eyes.check_region(${args})`)*/
            let Tag = !tag ? `` : `, tag="${tag}"`
            let MatchTimeout = !matchTimeout ? `` : `, match_timeout=${matchTimeout}`
            let fully = !isFully ? `` : `, stitch_content=${capitalizeFirstLetter(isFully)}`
            return addCommand(python`eyes.check_region(` + regionParameter(region) + Tag + MatchTimeout + fully + `)`)
        },
        checkRegionByElement(element, matchTimeout, tag) {
            return addCommand(python`eyes.checkRegionByElement(
        ${element},
        ${tag},
        ${matchTimeout},
      )`)
        },
        checkRegionBy(selector, tag, matchTimeout, stitchContent) {
            return addCommand(python`eyes.checkRegionByElement(
        ${selector},
        ${tag},
        ${matchTimeout},
        ${stitchContent},
      )`)
        },
        checkRegionInFrame(frameReference, region, matchTimeout, tag, isFully) {
            let Tag = !tag ? `` : `, tag="${tag}"`
            let MatchTimeout = !matchTimeout ? `` : `, match_timeout=${matchTimeout}`
            let fully = !isFully ? `` : `, stitch_content=${capitalizeFirstLetter(isFully)}`
            return addCommand(python`eyes.check_region_in_frame(` +
        	framesClassic(frameReference) + `, ` +
        	regionParameter(region) + Tag + MatchTimeout + fully + `)`
            )
        },
        close(throwEx = true) {
            let isThrow = throwEx.toString()
            return addCommand(python`eyes.close(raise_ex=` + isThrow[0].toUpperCase() + isThrow.slice(1) + `)`)
        },
        abort() {
            return addCommand(python`eyes.abort`)
        },
        locate(visualLocatorSettings) {
            return addCommand(python`eyes.locate(${visualLocatorSettings})`)
        },
        extractText(regions) {
            return addCommand(python`eyes.extract_text(${regions})`)
        }
    }

    const assert = {
        equal(actual, expected, message) {
            if ((expected && expected.isRef) && (JSON.stringify(expected) === undefined)) return addCommand(python`assert ${actual} == ` + expected.ref())
	    if (((typeof expected) === 'string') && (expected === 'true')) return addCommand(python`assert ${actual} == ${expected}, ${message}`)
	    return addCommand(python`assert ${actual} == ${directString(JSON.stringify(expected))}, ${message}`)
        },
        notEqual(actual, expected, message) {
            return addCommand(python`assert ${actual} != ${directString(JSON.stringify(expected))}, ${message}`)
        },
        ok(value, message) {
            return addCommand(python`assert ${value}, ${message}`)
        },
        instanceOf(object, className, message) {
            return addCommand(python`assert isinstance(${object}, ${directString(className)}), ${message}`)
        },
        throws(func, check) {
            let command
            if (check) {
                command = python`with pytest.raises(${check}):
                     ${func}`
            } else {
                command = python`with pytest.raises(Exception):${func}`
            }
            const commands = test.output.commands
            const initialLength = commands.length
            addCommand(command)
            commands.splice(commands.length - 1, 1)
            commands.forEach((el, index, arr) => {
                if (index > initialLength) arr[index] = `    ${el}`
            })
        },
    }

    const helpers = {
        getTestInfo(result) {
            return addCommand(python`get_test_info(eyes.api_key, ${result})`).type({
                type: 'TestInfo',
                schema: {
                    actualAppOutput: {
                        type: 'Array',
                        items: {
                            type: 'AppOutput',
                            schema: {
                                image: {
                                    type: 'Image',
                                    schema: {hasDom: 'Boolean'},
                                },
                                imageMatchSettings: {
                                    type: 'ImageMatchSettings',
                                    schema: {
                                        ignoreDisplacements: 'Boolean',
                                        ignore: {type: 'Array', items: 'Region'},
                                        floating: {type: 'Array', items: 'FloatingRegion'},
                                        accessibility: {type: 'Array', items: 'AccessibilityRegion'},
                                        accessibilitySettings: {
                                            type: 'AccessibilitySettings',
                                            schema: {
                                                level: 'AccessibilityLevel',
                                                version: 'AccessibilityGuidelinesVersion'
                                            },
                                        },
                                        layout: {type: 'Array', items: 'Region'}
                                    },
                                },
                            }
                        },
                    },
                },
            })
        },
	getDom(result, domId) {
		return addCommand(python`get_dom(${result}, ${domId})`).type({type: 'JsonNode'}).methods({
        getNodesByAttribute: (dom, name) => addCommand(python`getNodesByAttribute(${dom}, ${name});`).type({type: 'JsonNode'})})
	},
        math: {
                       round(number) {
                               return addCommand(python`round(${number})`)
                       },
               }
    }

    return {driver, eyes, assert, helpers}
}


function getVal(val) {
    let nameAndValue = val.toString().split("\"")
    return nameAndValue[1]
}

function setUpMobileNative(test, addHook) {
	addHook('beforeEach', python`@pytest.fixture(scope="function")`)
        addHook('beforeEach', python`def browser_type():`)
	addHook('beforeEach', python`    return "Appium"`)
	addHook('beforeEach', python`\n`)
}

function setUpWithEmulators(test, addHook) {
	if (test.env.device === 'Android 8.0 Chrome Emulator') {
				addHook('beforeEach', python`@pytest.fixture(scope="function")`)
        			addHook('beforeEach', python`def browser_type():`)
			        addHook('beforeEach', python`    return "ChromeEmulator"`)
				addHook('beforeEach', python`\n`)
            			addHook('beforeEach', python`@pytest.fixture(scope="function")`)
            			addHook('beforeEach', python`def emulation():`)
				addHook('beforeEach', python`    is_emulation = True`)
				switch (test.config.baselineName){
					case 'Android Emulator 8.0 Portrait mobile fully':
						addHook('beforeEach', python`    orientation = "Portrait"`)
						addHook('beforeEach', python`    page = "mobile"`)
						break;
					case 'Android Emulator 8.0 Portrait scrolled_mobile fully':
						addHook('beforeEach', python`    orientation = "Portrait"`)
						addHook('beforeEach', python`    page = "scrolled_mobile"`)						
						break;
					case 'Android Emulator 8.0 Portrait desktop fully':
						addHook('beforeEach', python`    orientation = "Portrait"`)
						addHook('beforeEach', python`    page = "desktop"`)
						break;
					default:
						throw Error(`Couldn't intrpret baselineName ${test.config.baselineName}. Code update is needed`)
				}
				addHook('beforeEach', python`    return is_emulation, orientation, page`)
				addHook('beforeEach', python`\n`)
			}
			else throw Error(`Couldn't intrpret device ${test.env.device}. Code update is needed`)
}

function setUpBrowsers(test, addHook) {
    let headless = ("env" in test) && ("headless" in test.env) && (test.env.headless === false)? false: true
    let legacy = ("env" in test) && ("legacy" in test.env) && (test.env.legacy === true)? true: false
    let css = ("stitchMode" in test.config) && (test.config.stitchMode.toUpperCase().localeCompare('CSS'))? true: false
    if (("env" in test) && ("browser" in test.env))
    {
        addHook('beforeEach', python`@pytest.fixture(scope="function")`)
        addHook('beforeEach', python`def browser_type():`)
        switch (test.env.browser){
          case 'firefox':
            addHook('beforeEach', python`    return "Firefox"`)
            addHook('beforeEach', python`\n`)
            addHook('beforeEach', python`@pytest.fixture(scope="function")`)
            addHook('beforeEach', python`def options():`)
            addHook('beforeEach', python`    return webdriver.FirefoxOptions()`)
            break;
          case 'ie-11':
            addHook('beforeEach', python`    return "IE11"`)
            break;
          case 'edge-18':
            addHook('beforeEach', python`    return "Edge"`)
            break;
          case 'safari-11':
            addHook('beforeEach', python`    return "Safari11"`)
            break;
          case 'safari-12':
            addHook('beforeEach', python`    return "Safari12"`)
            break;
          case 'chrome':
	    addHook('beforeEach', python`    return "Chrome"`)
            break;
          default:
            throw Error(`Couldn't intrpret browser type ${test.env.browser}. Code update is needed`)
        }
        if (legacy) {
	    addHook('beforeEach', python`\n`)
            addHook('beforeEach', python`@pytest.fixture(scope="function")`)
            addHook('beforeEach', python`def legacy():`)
            addHook('beforeEach', python`    return True`)
        }
        addHook('beforeEach', python`\n`)
    }
}



