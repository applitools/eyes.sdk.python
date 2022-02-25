## [5.1.0] - 2022-03-01
### Added
- Target selection in Shadow DOM [Trello 2822](https://trello.com/c/o3Cl5GT2)
### Fixed
- Restore VisualGridRunner agent id [Trello 2819](https://trello.com/c/c7NT1SAW)

## [5.0.5] - 2022-02-15
### Fixed
- Unable to set `device_name` in `applitools.yaml` [Trello 2810](https://trello.com/c/VFBCt2WF)

## [5.0.4] - 2022-02-10
### Fixed
- Eyes configured with n-versions-back UFG rendering targets raised an exception on open [Trello 2809](https://trello.com/c/pPSi5sDj)
- Specify supported python version via `Requires-Python` classifier [Trello 2804](https://trello.com/c/JNFbBD9G)

## [5.0.3] - 2022-02-04
### Fixed
- Custom configuration properties were incorrectly added to batch properties
- Unable to abort eyes after Runner.get_all_test_results call [Trello 1223](https://trello.com/c/rNUPtdAk)
- Eyes configuration can be set via Eyes.configuration property [Trello 1223](https://trello.com/c/rNUPtdAk)

## [5.0.2] - 2022-01-31
### Updated
- Allow installing with older appium and selenium on python>=3.7
### Fixed
- Eyes.locate unexpected None error when requested locator was not found [Trello 2796](https://trello.com/c/Uz5Y9Qqx)

## [5.0.1] - 2022-01-26
### Fixed
- [eyes-robotframework] Serialization of stitch_mode from `applitools.yaml`
- [eyes-robotframework] Update default viewport for `web_ufg` in `applitools.yaml`
- Error when trying to check target referenced By.ID selector [Trello 2794](https://trello.com/c/fh4C8EaY)

## [5.0.0] - 2022-01-24
### Added
- Library is now based on Universal SDK

## [4.25.3] - 2021-11-03
### Updated
- Avoid using deprecated desired_capabilities attribute of Selenium 4 webdriver [Trello 2742](https://trello.com/c/QbCUSeH2)

## [4.25.2] - 2021-10-15
### Fixed
- Appium EyesWebDriver crashes on user_agent access [Trello 2734](https://trello.com/c/OMkTvYDh)

## [4.25.1] - 2021-10-10
### Fixed
- Error when checking full element in mobile browsers [Trello 2716](https://trello.com/c/cOwG4zO6)
- [eyes-robotframework] No agent_id [Trello 2729](https://trello.com/c/xZUPhEfx)
- [eyes-robotframework] Not possible to assign batch info in `Eyes Open` [Trello 2730](https://trello.com/c/n6T8qzWK)
- [eyes-robotframework] Consistence usage of enums [Trello 2731](https://trello.com/c/AvrEdz8ck)

## [4.25.0] - 2021-09-09
### Added
- Eyes Robot Framework SDK [GH 377](https://github.com/applitools/eyes.sdk.python/pull/377)

## [4.24.3] - 2021-08-18
### Updated
- Debug logging in UFG resource downloader to aid stuck runner debugging [Trello 2684](https://trello.com/c/AC2WKrI7)

## [4.24.2] - 2021-08-12
### Fixed
- UFG test is aborted if render server responds with null render status [Trello 2689](https://trello.com/c/C8m6Fv4T)

## [4.24.1] - 2021-08-09
### Fixed
- False unclosed test warnings are printed for finished tests [Trello 2688](https://trello.com/c/fqzJhHo5)

## [4.24.0] - 2021-08-06
### Added
- Timeout argument and state logging to get_all_test_results method of runner [Trello 2684](https://trello.com/c/AC2WKrI7)

## [4.23.1] - 2021-07-21
### Fixed
- ClassicRunner stitching issue [Trello 2615](https://trello.com/c/PDgW2wuN)

## [4.23.0] - 2021-07-12
### Added
- [eyes-images] Support of searching region in OCRRegion [Trello 2663](https://trello.com/c/uGPDJpmI)
### Fixed
- Re-apply abort-on-error fixes avoiding aborting tests after close call [Trello 2612](https://trello.com/c/qBAEmMTQ) [Trello 2629](https://trello.com/c/BpDnwlCi)

## [4.22.3] - 2021-07-02
### Fixed
- Failure to capture regions on scrolled down page [Trello 2392](https://trello.com/c/PC2vRlqV)
- Revert 4.22.1 fixes as it caused tests to be aborted if abort was called after close_async [Trello 2654](https://trello.com/c/YewzI8IN)

## [4.22.2] - 2021-06-23
### Fixed
- Mobile Safari CSS stitching error [Trello 2614](https://trello.com/c/mmJnce9U)

## [4.22.1] - 2021-06-16
### Fixed
- UFG Tests stay in running state when render fails [Trello 2612](https://trello.com/c/qBAEmMTQ)
- UFG abort tests if captured CDT size is bigger than 30mb [Trello 2629](https://trello.com/c/BpDnwlCi)
- Attrs version incompatibility [Trello 2610](https://trello.com/c/BUHKASAz)

## [4.22.0] - 2021-06-07
### Added
- JS Layout breakpoints suport [Trello 2258](https://trello.com/c/3Ty3HRCG)
### Fixed
- Layout is skewed off coded selector [Trello 2583](https://trello.com/c/wxtUJtI5)

## [4.21.0] - 2021-05-28
### Added
- Allow Python Proxy via ProxySettings object [Trello 1583](https://trello.com/c/qQAooLih)
### Fixed
- Eyes stuck when stitching scrollable region on a scrolled down page [Trello 2568](https://trello.com/c/swDfXtGL)

## [4.20.1] - 2021-05-18
### Fixed
- Capture regions inside manually switched frames [Trello 2136](https://trello.com/c/bOYeHaoz)

## [4.20.0] - 2021-04-27
### Added
- Supporting agent_run_id and variant_id. [Trello 2527](https://trello.com/c/6SyxJXVZ)
### Fixed
- Viewport location algorithm fails on iPhone XR landscape screenshots [Trello 2559](https://trello.com/c/gsElVi8W)

## [4.19.0] - 2021-04-21
### Added
- Support of Custom Properties in BatchInfo [Trello 2445](https://trello.com/c/IKTydXLv)

## [4.18.4] - 2021-04-13
### Updated
- Send more data with Match Request [Trello 2454](https://trello.com/c/ekSr34zt)
- Automatic viewport position detection on iOS devices [Trello 2532](https://trello.com/c/inyVHzut)

## [4.18.3] - 2021-03-26
### Fixed
- [eyes-images] viewport not automatically set [Trello 2491](https://trello.com/c/G5GF7xa9)
- Check multiple times fails for some types of check [Trello 2476](https://trello.com/c/ipfT8z9h)
- Failed to set viewport size error [Trello 2483](https://trello.com/c/eP9yFbsP)

## [4.18.2] - 2021-03-19
### Fixed
- Use brotli library instead of brotlipy which fails to install on OSX [Trello 2503](https://trello.com/c/sudU9wjY)

## [4.18.1] - 2021-03-16
### Fixed
- CSS is not loaded properly using the UFG [Trello 2503](https://trello.com/c/sudU9wjY)

## [4.18.0] - 2021-03-11
### Added
- Browser cookies are used when UFG resources are downloaded [Trello 2433](https://trello.com/c/6OYDSI1Q)
### Updated
- Update missing types [Trello 2494](https://trello.com/c/pqcjOUkl) [Trello 2471](https://trello.com/c/aTDUpWIE)
- disable_browser_fetching configuration option is now True by default [Trello 2433](https://trello.com/c/6OYDSI1Q)
### Fixed
- UFG not loading resources with proxy [Trello 2433](https://trello.com/c/6OYDSI1Q)

## [4.17.1] - 2021-02-25
### Fixed
- Some checks in multi-checks tests might be skipped [Trello 2463](https://trello.com/c/YAMPDWIM)

## [4.17.0] - 2021-02-12
- Add extract_text_region for OCR support [Trello 2440](https://trello.com/c/FLGKnqIS)
### Updated
- Better logging to aid dom-capture script errors debugging [Trello 2457](https://trello.com/c/6CcbvxWU)

## [4.16.0] - 2021-02-05
### Added
- Add extract_text_region for OCR support [Trello 2440](https://trello.com/c/FLGKnqIS)
### Fixed
- Region screenshots not working with images.Eyes [Trello 2432](https://trello.com/c/VYqhbSIJ)

## [4.15.1] - 2021-01-27
### Added
- StdoutLogger accepts true/false for debug/info levels [Trello 376](https://trello.com/c/1xzNhRlm)
### Updated
- Structured logging [Trello 2395](https://trello.com/c/NuhnOCD6)
- DOM snapshot script to *4.4.8* [Trello 1835](https://trello.com/c/OyWRWqJm)

## [4.15.0] - 2021-01-11
### Added
- Concurrency version 2 protocol optimizations [Trello 2368](https://trello.com/c/0qi2c0jW)
- Retry on dom-snapshot frame capture error [Trello 2212](https://trello.com/c/iBY0LLki)
### Fixed
- Unable to capture multiple scrolled region screenshots [Trello 2397](https://trello.com/c/3RvCvojV)
### Updated
- DOM snapshot script to *4.4.3* [Trello 2405](https://trello.com/c/wBy9nGQi)

## [4.14.0] - 2020-12-25
### Added
- Add SAFARI_EARLY_ACCESS BrowserType [Trello 2385](https://trello.com/c/5PncFGDO)
- delete() method to TestResults class [Trello 2371](https://trello.com/c/d0OZ3bvH)
### Updated
- Updated concurrency model, added RunnerOptions [Trello 2152](https://trello.com/c/yNzhBkBh)
- DOM snapshot script to *4.4.1* [Trello 2370](https://trello.com/c/LtZ0SU2B) [Trello 2380](https://trello.com/c/yeMEtWhN)

## [4.13.2] - 2020-12-04
### Updated
- DOM snapshot script to *4.2.9* [Trello 2364](https://trello.com/c/97wQruS9)

## [4.13.1] - 2020-12-03
### Updated
- Temporarily disabled skip list [Trello 2363](https://trello.com/c/ynLHfleQ)
- DOM snapshot and DOM capture scripts to *4.2.8* and *8.0.1* [Trello 2364](https://trello.com/c/97wQruS9)

## [4.13.0] - 2020-11-25
### Added
- API to disable cross origin rendering [Trello 2346](https://trello.com/c/y7x48jmT)
### Fixed
- Steps/checks stuck in running state [Trello 2340](https://trello.com/c/yZUP5h0f)
### Updated
- Supporting iPhone 12 in `IosDeviceName` class. [Trello 2269](https://trello.com/c/yWFy2pRE)

## [4.12.0] - 2020-11-20
### Added
- Support cross origin iframes in UFG [Trello 551](https://trello.com/c/iJKPvd75)
- Add x-applitools-eyes-client-request-id header to API requests [Trello 2332](https://trello.com/c/yuBGjW6u)
- Add padding option to match regions [Trello 2337](https://trello.com/c/RNNcgMv7)
### Updated
- Pin keyring dependency for travis deploy stage. Update some tests [Trello 2309](https://trello.com/c/aIWIFRcY)
- Add more retries for connection to server [Trello 2335](https://trello.com/c/jVEn0ZfD)

## [4.11.5] - 2020-11-17
### Fixed
- Manually applied layout regions do not work on the Visual Grid [Trello 2317](https://trello.com/c/8qG51ind)
- Dom Snapshot Timeout exceptions on heavy pages [Trello 2227](https://trello.com/c/2AjLHPFw)

## [4.11.4] - 2020-11-11
### Fixed
- Target.region() outside of viewport on MobileSafari with iOS Simulator doesn't work correctly [Trello 1708](https://trello.com/c/wrMoRDPY)
- Parsing CSS has failed if `@charset` was present [Trello 2227](https://trello.com/c/2AjLHPFw)
### Updated
- Abort UFG test if dom-snapshot script failed [Trello 2227](https://trello.com/c/2AjLHPFw)
- Lifted pillow restriction to support python 3.9 [Trello 2303](https://trello.com/c/EcpNN2tY)

## [4.11.3] - 2020-11-03
### Fixed
- Native app error message on eyes.open [Trello 2291](https://trello.com/c/zS2Khlqq)

## [4.11.2] - 2020-11-01
### Fixed
- DOM-Snapshot hangs on pages with huge DOM [Trello 1983](https://trello.com/c/lOJ8QQse)
### Updated
- Restrict tinycss2 dependency below 1.1.0 as it breaks css parsing [Trello 2287](https://trello.com/c/7dilOPNv)

## [4.11.1] - 2020-10-29
### Updated
- New logs for printing dom snapshot result [Trello 2252](https://trello.com/c/7aalHb28)

## [4.11.0] - 2020-10-27
### Added
- Allow to disable fetching page resources by dom snapshot script [Trello 2242](https://trello.com/c/C1YodBjt)
### Fixed
- Coded Layout region placed in the wrong spot [Trello 2200](https://trello.com/c/4b40ZKOa)
- Resources grabbed from cached resources *are still sent* in the render's resource map [Trello 2129](https://trello.com/c/kCsU9aM4)

## [4.10.0] - 2020-10-16
### Added
- Supporting check full element with ufg [Trello 2145](https://trello.com/c/8tPAnz66)
### Fixed
- Incorrect Device Name send to Dashboard [Trello 1163](https://trello.com/c/4PPntuFb)
- Broken scaling on mobile native apps [Trello 465](https://trello.com/c/WS0XeAxs)
### Updated
- Problem with check window when driver context is Frame [Trello 1421](https://trello.com/c/zUnlId86)

## [4.9.0] - 2020-10-08
### Added
- Allow to call eyes.check(Target) without required tag parameter [Trello 1332](https://trello.com/c/eog9OcrR)
### Updated
- Added IosVersion for IosDeviceInfo [Trello 2187](https://trello.com/c/25AjSV6V)

## [4.8.3] - 2020-10-05
### Fixed
- Error in log file when checking a page with cors frames [Trello 2191](https://trello.com/c/DZ8HrDjm)
### Updated
- [UFG] Add non-200 URLs to resource map [Trello 1798](https://trello.com/c/urf8SY1Z)
- Print OS and Python versions to logs [Trello 2153](https://trello.com/c/ZBxxo3dn)
- Add missing test for set_viewport_size [Trello 1919](https://trello.com/c/9vRolTeu)

## [4.8.2] - 2020-09-22
### Fixed
- Uploading of big resources breaks rendering in UFG [Trello 2154](https://trello.com/c/rBYpPkqT)
### Updated
- Update implementation of dom_capture to use the latest dom-capture js script [Trello 2146](https://trello.com/c/SPuY0Hmb)
- Change guidelines_version to version in SessionAccessibilityStatus [Trello 1890](https://trello.com/c/q9xRauk7)

## [4.8.1] - 2020-09-18
### Fixed
- Missing match regions on UFG with Python 2 [Trello 2020](https://trello.com/c/PD67n1Vj)
### Updated
- Add additional domains and app names information [Trello 870](https://trello.com/c/8X8mwBMS)
- Internal test infrastructure update [Trello 2147](https://trello.com/c/HVpkukIW) [GitHub 237](https://github.com/applitools/eyes.sdk.python/pull/237) [GitHub 232](https://github.com/applitools/eyes.sdk.python/pull/232)

## [4.8.0] - 2020-09-07
### Added
- VisualGrid Options [Trello 2089](https://trello.com/c/d4zggQes)
### Updated
- Added `name` and `names` to VisualLocatorSettings [Trello 2077](https://trello.com/c/smh8LdKv)

## [4.7.1] - 2020-08-25
### Fixed
- Match level have been changed automatically when call match region [Trello 2104](https://trello.com/c/5pXHlas3)
### Updated
- Remove typing annotation that Enum accepts Text [Trello 2076](https://trello.com/c/zZ0oTowF)
- Remove DOM-Snapshot and DOM-Capture from being tracked in Git [Trello 2099](https://trello.com/c/9T9gltjj)

## [4.7.0] - 2020-08-10
### Added
- Allow to setup custom server connector [Trello 2055](https://trello.com/c/TIQVZQrK)
- Public interface to set debug screenshots provider [Trello 2058](https://trello.com/c/olI8Gy6S)
### Updated
- Screenshot retry mechanism is now more efficient [Trello 1866](https://trello.com/c/KyxkI6Bu)
- Limited screenshot size. [Trello 1991](https://trello.com/c/2iCNfoI7)
- Add missing typedef for Visual Locators type [Trello 2069](https://trello.com/c/pvV5duI4)

## [4.6.2] - 2020-07-30
### Fixed
- UFG Bad DOM Rendering of Salesforce page [Trello 1899](https://trello.com/c/wfQzNryP)
- The internal objects inside of Configuration properties wasn't copied properly [Trello 2010](https://trello.com/c/ovjgBPJW)
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
