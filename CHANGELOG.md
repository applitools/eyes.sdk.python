## [vNext]
### Fixed
- UFG Bad DOM Rendering of Salesforce page [Trello 1899](https://trello.com/c/wfQzNryP)
### Updated
- DOM snapshot scripts to *4.0.1*

## [4.6.1] - 2020-07-29
### Fixed
- Randomly render errors and skip list issue on UFG [Trello 2044](https://trello.com/c/IObN01t2)
- Unicode issues with UFG and Windows [Trello 2027](https://trello.com/c/2JSXFdde)
### Updated
- Improve indication that app_name and/or test_name are missing [Trello 2038](https://trello.com/c/YtuycQpX)

## [4.6.0] - 2020-07-23
### Added
- Skip list for DOM snapshot [Trello 1974](https://trello.com/c/44xq8dze)
### Updated
- DOM snapshot scripts to *3.7.1*

## [4.5.0] - 2020-07-20
### Fixed
- clear_properties method missing in UFG [Trello 2010](https://trello.com/c/ovjgBPJW)
### Added
- Additional strategy to set viewport size [Trello 1919](https://trello.com/c/9vRolTeu)
- Option for use latest available versions of libraries for Py3 [Trello 2008](https://trello.com/c/mt8wSiQC)
- Visual Viewport support for UFG [Trello 1957](https://trello.com/c/jWvdBwex)
### Updated
- Improved traceback info for Configuration.add_browser/s() and match regions [Trello 1998](https://trello.com/c/8IoYsgNI)
- Increased backoff for uploading to Storage Service [Trello 2001](https://trello.com/c/Em7MvWXs)

## [4.4.2] - 2020-07-10
### Updated
- Remove get\set_viewport_size from Eyes images [Trello 1413](https://trello.com/c/v32N4D8S)
- Added missing `stitching_service` URI field in `RenderRequest`. [Trello 1988](https://trello.com/c/Yr6EsUlL)
- DOM snapshot scripts to *3.5.3* [Trello 1865](https://trello.com/c/haTeCXzq)

## [4.4.1] - 2020-07-01
### Updated
- Add additional devices support to the DeviceName ENUM [Trello 1751](https://trello.com/c/JOyUqzEM)

## [4.4.0] - 2020-06-25
### Added
- Support of visual locators [Trello 1754](https://trello.com/c/S1xgtP7A)
### Updated
- Removed `IosScreenOrientation` enum in favor of existing `ScreenOrientation` enum due to same viewports issue. [Trello 1944](https://trello.com/c/EzyG7525)

## [4.3.1] - 2020-06-18
### Updated
- Internal changes for ticket [Trello 1872](https://trello.com/c/bykk2rzB)
### Fixed
- Match regions returns incorrect number of regions [Trello 1911](https://trello.com/c/5Y4rZAX6)
- element.find_element(s) search element(s) on full source page instead of inner element [Trello 1830](https://trello.com/c/s5W2pnUT) [GH #189](https://github.com/applitools/eyes.sdk.python/pull/189)

## [4.3.0] - 2020-06-05
### Fixed
- Error for using EDGE is thrown with no reason - Python [Trello 1873](https://trello.com/c/DRavDAzS)
### Added
- Supported rendering on ios simulators. [Trello 1872](https://trello.com/c/bykk2rzB)

## [4.2.1] - 2020-05-27
### Fixed
- dir(eyes_driver) and dir(eyes_element) call on Python 2 raise an error [Trello 1879](https://trello.com/c/5qjuqVw9) [GH #174](https://github.com/applitools/eyes.sdk.python/pull/174)
- element.find_elements call raise an error [Trello 1830](https://trello.com/c/s5W2pnUT) [GH #174](https://github.com/applitools/eyes.sdk.python/pull/174)
- All New tests was marked as Unresolved [Trello 1841](https://trello.com/c/boxDvmMW) [GH #176](https://github.com/applitools/eyes.sdk.python/pull/176)
- UFG test is not rendered if content-type is None [Trello 1836](https://trello.com/c/2IK1o3Qd) [GH #179](https://github.com/applitools/eyes.sdk.python/pull/179)

## [4.2.0] - 2020-05-18
### Added
- Accessibility Validation feature [Trello 1767](https://trello.com/c/gq69woeK)
### Fixed
- element.find_element call raise an error; driver.switch_to.window if prev tab was closed raise an error [Trello 1794](https://trello.com/c/cRcp2T5n)
### Updated
- Add tag release event [Trello 1758](https://trello.com/c/Jograd5k)

## [4.1.25] - 2020-04-24
### Added
- UFG Edge Chromium support [Trello 1757](https://trello.com/c/LUe43aee)
### Fixed
- StartSession request now considers "isNew" flag. [Trello 1715](https://trello.com/c/DcVzWbeR)
### Updated
- All SDKs should report their version in all requests to the Eyes server [Trello 1697](https://trello.com/c/CzhUxOqE) [GH #153](https://github.com/applitools/eyes.sdk.python/pull/153)

## [4.1.24] - 2020-03-30
### Fixed
- Tests doesn't work with Python 2 when coded region is used [Trello 1684](https://trello.com/c/K1Bv5OK7) [GH #146](https://github.com/applitools/eyes.sdk.python/pull/146)
- Custom methods and attributes that was added to ChromeDriver wasn't accessible from EyesWebDriver instance [Trello 1602](https://trello.com/c/aMbwNDUF) [GH #150](https://github.com/applitools/eyes.sdk.python/pull/150)

## [4.1.23] - 2020-03-25
### Fixed
- VG tests hang intermittently [Trello 1566](https://trello.com/c/kU2EaDiE)

## [4.1.22] - 2020-03-18
### Fixed
- Issue With VG Capturing After Element Check [Trello 1639](https://trello.com/c/tPRpKuOX)
- VG Ignore region in the wrong coordinates [Trello 1654](https://trello.com/c/OvhH1p91)

## [4.1.21] - 2020-03-16
### Fixed
- Handling Data URL in CSS [Trello 1656](https://trello.com/c/DlBLzq0R)

## [4.1.20] - 2020-03-13
### Fixed
- Missing useragent in headers during downloading of resources for VG [Trello 1646](https://trello.com/c/QvI2Ba21)

## [4.1.19] - 2020-03-11
### Fixed
- Appium Native tests fail with error [Trello 1590](https://trello.com/c/gG26XQLH)

## [4.1.18] - 2020-03-06
### Fixed
- Non consistent execution of tests with VG [Trello 1623](https://trello.com/c/2s6WMVKn)
- get_all_test_results return always one TestResults object
### Updated
- Dom snapshot updated to *3.3.3* [Trello 1586](https://trello.com/c/ZS0Wb1FN)

## [4.1.17] - 2020-03-05
### Updated
- DOM directly to storage service on MatchWindow. [Trello 1592](https://trello.com/c/MXixwLnj)
- DOM capture and snapshot scripts to *7.1.3* and *1.4.9* respectively
### Fixed
- Requirements issue with attrs [Trello 1578](https://trello.com/c/sR56FqO7)
- VG not rendering properly with external css which contain relative resources [Trello 1619](https://trello.com/c/F2jfilLk)

## [4.1.16] - 2020-02-24
### Fixed
- Batch notification is not working if batch id contains some non URL-compatible symbols [Trello 1567](https://trello.com/c/hCPqs80W)

## [4.1.15] - 2020-02-20
### Fixed
- execute_script of EyesWebDriver not work with EyesWebElement [Trello 112](https://trello.com/c/OrdYpmTj)
- The `TypeError: integer argument expected, got float` was raised in some cases  [Trello 1536](https://trello.com/c/ZgU3wMR8)
- Set is_disabled cause an error [Trello 611](https://trello.com/c/eZBMTKHK)

## [4.1.14] - 2020-02-12
### Fixed
- Python SDK crashed on get RenderInfo with new server version [Trello 1555](https://trello.com/c/8DppLbN7)

## [4.1.13] - 2020-02-12
### Updated
- Allow to set api_key and server_url after set_batch_ids in BatchClose [GitHub 106](https://github.com/applitools/eyes.sdk.python/pull/106)
### Fixed
- DefaultMatchSettings being overridden incorrectly by ImageMatchSettings [Trello 1495](https://trello.com/c/KEbWXavV)
- "Got an empty screenshot window!" with viewport screenshot [GitHub 107](https://github.com/applitools/eyes.sdk.python/pull/107)

## [4.1.12] - 2020-02-07
### Update
- Pin Appium Python Client to 4+ version
- The ServerConnector now utilize HTTP Session [GitHub 101](https://github.com/applitools/eyes.sdk.python/pull/101)
### Fixed
- Wrong object inside TestsResults.steps_info
### Added
- Batch Notifications [Trello 1380](https://trello.com/c/gare3CuF)

## [4.1.11] - 2020-01-30
### Updated
- Use start_session and render_info as long requests

## [4.1.10] - 2020-01-28
### Added
- Uploading images directly to data storage server [Trello 1461](https://trello.com/c/1V5X9O37)
### Fixed
- Same test on different browsers (VG) are splitted to different batches if batch name isn't configured explicitly [Trello 1498](https://trello.com/c/IuKjOQQG)

## [4.1.9] - 2020-01-21
### Fixed
- Typo in BrowserType
- Prevent to download resources with urls that starts from `data:`
- Creating VGResource with Python 2

## [4.1.8] - 2020-01-20
### Updated
- Visual Grid: Added older versions support for Chrome, Firefox and Safari browsers. [Trello 1479](https://trello.com/c/kwsR1zql)

## [4.1.7] - 2020-01-17
### Fixed
- Dependencies warning at runtime [Trello 1476](https://trello.com/c/Rmqo8HPM)
- Infinite loop during render when opened without viewport size [#90](https://github.com/applitools/eyes.sdk.python/pull/90)

## [4.1.6] - 2020-01-08
### Fixed
- Multiple instances opening on Windows [Trello 1457](https://trello.com/c/noYzDV70)

## [4.1.5] - 2020-01-08
### Fixed
- Wrong screenshot location when using .fully() [Trello 1455](https://trello.com/c/veMyZsyg)
- Handling setoverflow [Trello 1448](https://trello.com/c/cIgjp0z6)
- Broken By.XPATH select in fluent interface [Trello 1452](https://trello.com/c/R0bFRpSc)

## [4.1.4] - 2019-12-30
### Added
- Support SVG resource fetching [Trello 193](https://trello.com/c/nZdODyjL)

## [4.1.3] - 2019-12-20
### Fixed
- Python SDK was abort_async [Trello 1090](https://trello.com/c/SCsMv6JN)
- (selenium) Not working switching to previous context after check [Trello 1262](https://trello.com/c/YoGEYS09)
- (visualgrid) Test should be aborted if rendering failed [Trello 46](https://trello.com/c/diOQDnzi)

## [4.1.2] - 2019-12-15
### Added
- Fluent interface for Configuration [Trello 1407](https://trello.com/c/KUCeFzik)
### Fixed
- Call of eyes.get_configuration() raises exception [Trello 1405](https://trello.com/c/QUiQG4RI)

## [4.1.1] - 2019-12-10
### Fixed
- eyes get/set_configuration() was returning configuration instance instead of clone [Trello 1378](https://trello.com/c/WtnHxRzD)
- Classic Runner get_all_test_results() Throws type error [Trello 1381](https://trello.com/c/kJJBEu4M)

## [4.1.0] - 2019-12-9
### Fixed
- app_urls and api_urls were always None in TestResults
- Validation error when passing RectangleSize as viewport_size in Configuration
- CSS scrolling in chrome 78. [Trello 1206](https://trello.com/c/euVqe1Sv)
- Rotation on mobile is broken [Trello 1354](https://trello.com/c/hS6Lv8PT)
- Capturing iframe's with VG [Trello 1356](https://trello.com/c/J5so3FDN)
- VG test don't run correctly with multiple Eyes [Trello 1329](https://trello.com/c/6KHE8FAO)
### Added
- Match region support in VG
- Check region support in VisualGrid client [Trello 1360](https://trello.com/c/rFOwfgwA)
- DomCapture 7.0.22, DomSnapshot 1.4.8 [Trello 1227](https://trello.com/c/d5hmB3gG)
- ClassicRunner [Trello 1093](https://trello.com/c/DxBia1UC)
- Type hints for Target class.
- Allow to get/set Configuration in Eyes with methods.
- This CHANGELOG file.
