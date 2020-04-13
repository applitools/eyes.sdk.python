## Fixed
- StartSession request now considers "isNew" flag. [Trello 1715](https://trello.com/c/DcVzWbeR)
# Updated
- All SDKs should report their version in all requests to the Eyes server [Trello 1697](https://trello.com/c/CzhUxOqE) [GH #153](https://github.com/applitools/eyes.sdk.python/pull/153)

# [4.1.24] - 2020-03-30
## Fixed
- Tests doesn't work with Python 2 when coded region is used [Trello 1684](https://trello.com/c/K1Bv5OK7) [GH #146](https://github.com/applitools/eyes.sdk.python/pull/146)
- Custom methods and attributes that was added to ChromeDriver wasn't accessible from EyesWebDriver instance [Trello 1602](https://trello.com/c/aMbwNDUF) [GH #150](https://github.com/applitools/eyes.sdk.python/pull/150)

# [4.1.23] - 2020-03-25
## Fixed
- VG tests hang intermittently [Trello 1566](https://trello.com/c/kU2EaDiE)

# [4.1.22] - 2020-03-18
## Fixed
- Issue With VG Capturing After Element Check [Trello 1639](https://trello.com/c/tPRpKuOX)
- VG Ignore region in the wrong coordinates [Trello 1654](https://trello.com/c/OvhH1p91)

# [4.1.21] - 2020-03-16
## Fixed
- Handling Data URL in CSS [Trello 1656](https://trello.com/c/DlBLzq0R)

# [4.1.20] - 2020-03-13
## Fixed
- Missing useragent in headers during downloading of resources for VG [Trello 1646](https://trello.com/c/QvI2Ba21)

# [4.1.19] - 2020-03-11
## Fixed
- Appium Native tests fail with error [Trello 1590](https://trello.com/c/gG26XQLH)

# [4.1.18] - 2020-03-06
## Fixed
- Non consistent execution of tests with VG [Trello 1623](https://trello.com/c/2s6WMVKn)
- get_all_test_results return always one TestResults object
## Updated
- Dom snapshot updated to *3.3.3* [Trello 1586](https://trello.com/c/ZS0Wb1FN)

# [4.1.17] - 2020-03-05
## Updated
- DOM directly to storage service on MatchWindow. [Trello 1592](https://trello.com/c/MXixwLnj)
- DOM capture and snapshot scripts to *7.1.3* and *1.4.9* respectively
## Fixed
- Requirements issue with attrs [Trello 1578](https://trello.com/c/sR56FqO7)
- VG not rendering properly with external css which contain relative resources [Trello 1619](https://trello.com/c/F2jfilLk)

# [4.1.16] - 2020-02-24
## Fixed
- Batch notification is not working if batch id contains some non URL-compatible symbols [Trello 1567](https://trello.com/c/hCPqs80W)

# [4.1.15] - 2020-02-20
## Fixed
- execute_script of EyesWebDriver not work with EyesWebElement [Trello 112](https://trello.com/c/OrdYpmTj)
- The `TypeError: integer argument expected, got float` was raised in some cases  [Trello 1536](https://trello.com/c/ZgU3wMR8)
- Set is_disabled cause an error [Trello 611](https://trello.com/c/eZBMTKHK)

# [4.1.14] - 2020-02-12
### Fixed
- Python SDK crashed on get RenderInfo with new server version [Trello 1555](https://trello.com/c/8DppLbN7)

# [4.1.13] - 2020-02-12
### Updated
- Allow to set api_key and server_url after set_batch_ids in BatchClose [GitHub 106](https://github.com/applitools/eyes.sdk.python/pull/106)
### Fixed
- DefaultMatchSettings being overridden incorrectly by ImageMatchSettings [Trello 1495](https://trello.com/c/KEbWXavV)
- "Got an empty screenshot window!" with viewport screenshot [GitHub 107](https://github.com/applitools/eyes.sdk.python/pull/107)

# [4.1.12] - 2020-02-07
## Update
- Pin Appium Python Client to 4+ version
- The ServerConnector now utilize HTTP Session [GitHub 101](https://github.com/applitools/eyes.sdk.python/pull/101)
## Fixed
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
