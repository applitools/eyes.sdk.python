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
