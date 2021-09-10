# The EyesLibrary configuration file v1.0

The Robot Eyes configuration file allows you to control various aspects of Eyes testing. The file is in YAML format.

## The configuration file content
You can check the latest configuration file by the [link](https://github.com/applitools/eyes.sdk.python/blob/develop/eyes_robotframework/src/EyesLibrary/applitools.yaml). If you have installed `EyesLibrary` you could initialize the config file with command: `python -m EyesLibrary init-config`.

The `applitools.yaml` has several top sections:
* [Shared settings](#shared-section)
* web: [Web settings](#web-settings)
* mobile_native: [Mobile native settings](#mobile-native-settings)
* web_ufg: [Ultrafast grid settings](#ultrafast-grid-settings)

The shared settings provide defaults for all run types. The other sections are for specific types of runs and define their configuration values. By default, they inherit the shared settings, but they can override any configuration if necessary.


### Shared section
The following fields can appear top-level of applitools.yaml config. Unless noted otherwise, you may also set these values under the other top-level fields ( *web*, *mobile_native* and *selenium_ufg*) to define the value when working in that specific mode:

#### server_url
```yaml
server_url: https://my.applitoolsserver.com
```
Use this example to define the URL of your Eyes server. If you have an on-prem server or private cloud, you must specify this. If you use the public Eyes server (https://eyesapi.applitools.com), then setting this key is optional since this is the default value. If you set the environment variable `APPLITOOLS_SERVER_URL` to the server URL, then Eyes uses that value as the default.

### api_key
```yaml
api_key: YOUT_API_KEY
```
You must set this value to your Eyes API key. See [How to obtain your API key] for details.

### app_name
```yaml
app_name: my app name
```
Set the value of the application name property. The application name is one of the five properties that define the baseline. The application name provides the scope to the test name, and tests can be grouped and managed on a per-application basis. See [The Apps & tests page] for details.

### viewport_size
```yaml
viewport_size:
    width: 1920
    height: 1080
```
Set the viewport size to be used by the browser for the test. The viewport size sets the browser window size, and it is also one of the five values that defines the baseline – the set of images against which this test is checked. See [Working with baselines] for more details.

### batch
```yaml
batch:  #optional
    id: YOUR_BATCH_ID
    name: YOUR_BATCH_NAME
    batch_sequence_name: YOUR_BATCH_SEQUENCE_NAME
    properties:
    - name: BatchPropery 1
      value: some value 1
    - name: BatchPropery 2
      value: some value 2
```
Set the name of the batch. In the Test manager, all of the results of tests that were executed as a single batch are displayed together and can be managed and operated on as a group. See [How to organize your tests with batches] for more details.
* id: Specify the ID explicitly (optional) – see [Batching tests in a distributed environment] for more details.
* batch_sequence_name: For detailed analysis across batches. See [Insights batch statistics] for more details.
* properties: The key/value pairs you define can be viewed as part of the batch properties in the Test manager and can be used for filtering and grouping. See [Using user-defined batch properties] for more details.

### branch_name
```yaml
branch_name: YOUR_BRANCH_NAME
```
Set the branch to be used as the baseline of the run. The use of a branch in Eyes corresponds to the use of a branch in the source code version control repository. The branch stores one or more baselines. Typically, every version of your software that runs on a source control branch has a corresponding Eyes branch that stores the Eyes baselines that represent the expected results of tests running on that software branch.

If the branch exists, and a matching baseline exists in the branch, then it is used as the basis for comparing the checkpoint images. If the branch does not exist yet and a parent branch, defined by the `parent_branch_name` value, exists and has a matching baseline, then that baseline is used. Otherwise, the default branch is used. The branch named by the `branch_name` value is actually created when you view the tests results of a run on this branch, make some changes (i.e. [accept a new, changed, or deleted step]), and do a [save operation].

### parent_branch_name
```yaml
parent_branch_name: YOUR_PARENT_BRANCH_NAME
```
Set the parent branch from which newly created branches get their initial baseline. See the explanation of the `branch_name` for more details.

### baseline_branch_name
```yaml
baseline_branch_name: YOUR_BASELINE_BRANCH_NAME
```
Set the name of the branch that the baseline reference is taken from and to which new and accepted steps are saved to.The baseline must exist. See [Copying baselines between branches] to discover how to create such a branch from existing baselines in existing branches. Do not use this option if you are using the `branch_name` option.

### baseline_env_name
```yaml
baseline_env_name: YOUR_BASELINE_ENV_NAME
```
Set this value to specify the name of the environment used to determine the baseline.

Eyes stores a set of mappings from an environment name to an environment E, where E is defined as a triplet <OS, Browser, ViewportSize>. You can specify that Eyes uses the baseline defined by the environment name instead of the test environment by assigning this value to the name of the environment.

### save_diffs
```yaml
save_diffs: true
```
Set this value to `true` to specify that steps that have mismatches should be automatically saved to the baseline.

In the usual workflow, if Eyes finds mismatches, you use the Test Manager to view the mismatches, accept or reject the steps with mismatches, and then update the baseline with the images captured in the accepted steps. This method allows you to instruct Eyes so that where steps have mismatches, or where there are new or missing steps, the corresponding steps in the baseline should be updated with the images captured in the current run of the test.

```
Setting this value to true, completely overwrites your baseline. It is usually preferable to see the results in the Test Manager and, if necessary, to accept all differences there. If you do use this method in a particular circumstance, remember to disable this setting for every day use.
```

### match_timeout
```yaml
match_timeout: 600
```
Set this value to specify the maximum amount of time Eyes should try to perform a match on the fully captured image.

Since a browser can take time to render a page (because it is complex, or because of slow network speeds), if Eyes detects mismatches, it initially assumes that the mismatch is because the render has not completed yet, and it retries the match after a short wait. You can set this value to determine how much time Eyes spends retrying the matching before declaring a mismatch.

### proxy
```yaml
proxy:
   url: "http://someproxy-url.com"
   host: myhostid
   port: 7200
   username: my name
   password: this is my secret password
```
If you run tests behind a firewall that can't access the Eyes server directly, then you can define a proxy server, and the commands are sent to the Eyes server via the proxy server. You must specify the URL. You only need the host, port, username, and password if they are required by the proxy server.

### save_new_tests
```yaml
save_new_tests: false
```
Set this value to `false` to specify that 'new' tests should not be automatically saved to the baseline by default.
This option is enabled by default (i.e. new tests are saved automatically to the baseline), so use this method to disable the default behavior.

### properties
```yaml
properties:
  - name: YOUR_PROPERTY_NAME
    value: YOUR_PROPERTY_VALUE
```
Set a list of user-defined properties, each of which is a key/value pair. These properties are defined as properties of the test as opposed to batch properties.

You can [view these properties] and use them to [filter] and [group] tests and steps in the Test manager.

## Web settings
Desktop and mobile browsers with Selenium and Appium.

### force_full_page_screenshot
```yaml
web:
  force_full_page_screenshot: true
```
By default, Eyes only captures the image visible in the browser viewport. If you set this value to true, Eyes captures and checks all of the content on the web page (anything accessible by scrolling the top-level element).

### wait_before_screenshots
```yaml
web:
  wait_before_screenshots: 100
```
Set this value to specify the amount of time (in milliseconds) that Eyes should wait before capturing a screenshot. This can be used if the image takes time to stabilize if, for example, there is an animation, meaning there is no synchronous way to wait for the image to be stable before calling the checkpoint command.

When a large image is captured with multiple sub-images using scrolling and stitching, Eyes waits the amount of time specified by this method before capturing each sub-image. Setting a value less than or equal to zero sets the default wait time.

### stitch_mode
```yaml
web:
  stitch_mode: CSS  # Scroll | CSS
```
When you set `force_full_page_screenshot` to true, Eyes captures the entire page, element, or frame by capturing multiple images across the page and stitching them together. The stitch mode defines the method for doing this. The default value is `Scroll`, but the recommended value is `CSS`.

### hide_scrollbars
```yaml
web:
  hide_scrollbars: true
```
Set this value to `true` so that Eyes hides the scrollbars before capturing screenshots, or set it to `false` to disable hiding the scrollbars. Hiding the scrollbars is recommended to avoid false mismatches caused by differences in the scrollbar position each time the checkpoint is captured and checked.

### hide_caret
```yaml
web:
  hide_caret: true
```
Set this value to true so that Eyes hides the cursor before the screenshot is captured. This is recommended to avoid mismatch artifacts caused by a blinking cursor.

### Mobile native settings
Mobile apps with Appium.
### is_simulator
```yaml
mobile_native:
  is_simulator: true
```
Set this value to `true` when the device under test is a simulator and not a real device. Eyes needs this information in order to operate correctly.

### Ultrafast grid settings

### runner_options
```yaml
web_ufg:
   runner_options:
      test_concurrency: 5
```
Set the maximum number of Eyes tests that can run concurrently when using the Ultrafast Grid.

### visual_grid_options
```yaml
web_ufg:
   visual_grid_options:
   - key: YOUR_VISUAL_GRID_OPTION
     value: YOUR_VISUAL_GRID_OPTION_VALUE
```
Set this value to pass an option of the Ultrafast grid. For a list of possible values, see [visual_grid_options property].

### disable_browser_fetching
```yaml
web_ufg:
  disable_browser_fetching: true
```
Under some circumstances, rendering of some resources may be missing. Set this value to `true` to eliminate these problems.

### enable_cross_origin_rendering
```yaml
web_ufg:
  enable_cross_origin_rendering: false
```
Normally, when a webpage contains content from multiple sites, rendering of the page succeeds. If there are rendering errors due to incorrect rendering of content from other sites, set this value to `false`. When you do this, iframes that originate from other websites are rendered as blank pages.

### dont_use_cookies
```yaml
web_ufg:
  dont_use_cookies: false
```
By default, cookie information in the browser is sent to the Ultrafast grid. Set this value to `true` to disable sending cookie information when sending checkpoint resources to the Ultrafast grid.

### layout_breakpoints
```yaml
web_ufg:
  layout_breakpoints: true
```
Configure the SDK to capture multiple DOM images for multiple viewport sizes.

When the test loads a page into the test browser, the test browser loads the page, executes any JavaScript loaded with that page, and creates a DOM. The SDK then sends this DOM to the Ultrafast Grid, where it is rendered for each configured execution environment.

When the Ultrafast Grid sizes the browser, device emulator, or simulator to match the viewport size of the execution environment, all CSS is applied so that any viewport-width-dependent layouts have the expected effect. However, the on-page JavaScript is not executed. If the JavaScript impacts the DOM and is viewport-width-dependent, then the page may be rendered incorrectly.

Setting this field to `true` allows you to request that the SDK resize the test browser viewport to multiple viewport widths. Resizing the test browser viewport triggers re-execution of the on-page JavaScript and the creation of a viewport-width-specific DOM. The SDK then sends all of these DOMs to the Ultrafast Grid and the Ultrafast Grid renders each execution environment using the DOM that matches the environment viewport width of the execution environment.

Setting this YAML value to `true` enables this feature and extracts a DOM for every distinct viewport size configured. Alternatively, you can pass a list of distinct viewport widths, in which case the DOM is extracted for those particular viewport widths.

See [Handling viewport-dependent JavaScript] for more details.


### Setting the Ultrafast grid execution environments
When using the Ultrafast grid, you must specify one or more execution environments. There are three types of environment, each with a list of supported devices. The three types are defined by the YAML fields `web_ufg:browsers:desktop` for a list of desktop browsers, `web_ufg:browsers:ios` IOS device simulation, and `web_ufg:browsers:chrome_emulation` for Chrome emulation.

#### desktop
```yaml
web_ufg:
  browsers:
    desktop:
      - browser_type: CHROME  # values from BrowserType
        width: 1900
        height: 1800
```
For each browser, specify the browser type and the viewport width and height.

#### ios
```yaml
web_ufg:
  browsers:
    ios:
    - device_name: iPhone_12_Pro  # names from IosDeviceName
      screen_orientation: PORTRAIT  # PORTRAIT | LANDSCAPE
      ios_version: LATEST  # LATEST | ONE_VERSION_BACK
```
For each IOS device to be simulated, specify the device name, the screen orientation (`PORTRAIT` or `LANDSCAPE`), and the ios version (`LATEST` or `ONE_VERSION_BACK`).


#### chrome_emulation
```yaml
web_ufg:
  browsers:
    chrome_emulation:
      - device_name: iPhone_4  # names from DeviceName
        screen_orientation: PORTRAIT  # PORTRAIT | LANDSCAPE
```
For each device to be emulated using the Chrome emulator, specify the device name and the screen orientation (`PORTRAIT` or `LANDSCAPE`).


[How to obtain your API key]: https://applitools.com/docs/topics/overview/obtain-api-key.html
[The Apps & tests page]: https://applitools.com/docs/topics/test-manager/pages/tm-page-apps-and-tests.html
[Working with baselines]: https://applitools.com/docs/topics/general-concepts/about-baselines.html
[How to organize your tests with batches]: https://applitools.com/docs/topics/working-with-test-batches/working-with-test-batches-in-overview.html
[Batching tests in a distributed environment]: https://applitools.com/docs/topics/working-with-test-batches/batching-tests-in-a-distributed-environment.html
[Insights batch statistics]: https://applitools.com/docs/topics/test-manager/pages/page-insights/tm-page-insights-batches.html
[Using user-defined batch properties]: https://applitools.com/docs/topics/working-with-test-batches/using-batch-properties.html
[accept a new, changed, or deleted step]: https://applitools.com/docs/topics/test-manager/pages/page-test-results/tm-accepting-and-rejecting-steps.html
[save operation]: https://applitools.com/docs/topics/test-manager/pages/page-test-results/tm-update-the-baseline.html
[Copying baselines between branches]: https://applitools.com/docs/topics/test-manager/howto/copying-baselines-between-branches.html
[view these properties]:https://applitools.com/docs/topics/test-manager/viewers/tm-viewer-test-details.html
[filter]: https://applitools.com/docs/topics/test-manager/pages/page-test-results/test-results-filter.html
[group]: https://applitools.com/docs/topics/test-manager/pages/page-test-results/test-results-grouping.html
[visual_grid_options property]: https://applitools.com/docs/api/eyes-sdk/classes-gen/class_configuration/method-configuration-visualgridoptions-selenium-python_sdk4.html
[Handling viewport-dependent JavaScript]: https://applitools.com/docs/topics/sdk/viewport-dependent-js.html
