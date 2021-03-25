module.exports = {
    'should handle check of stale element in frame if selector is preserved': {skipEmit: true, skip: true},
    'should extract text from regions': {skipEmit: true, skip: true},
    'should extract text regions from image': {skipEmit: true}, // Not implemented yet
    'check region by selector in frame multiple times with scroll stitching': {skip: true},	//problems in SDK to check multiple times
    'check region by selector in overflowed frame with scroll stitching': {skip: true},		//OutOfBoundsError: Region [Region(20, 708, 450 x 282, CONTEXT_RELATIVE)] is out of screenshot bounds [Region(0, 0, 700 x 460, SCREENSHOT_AS_IS)]
    'check region by selector in overflowed frame with vg': {skip: true},			//Unable to locate element: {"method":"css selector","selector":"img"}
    'check frame after manual switch to frame with css stitching classic': {skip: true},	//Stale element, but with driver2 it works with diffs
    'check frame after manual switch to frame with scroll stitching classic': {skip: true},	//Stale element, but with driver2 it works with diffs
    'check frame after manual switch to frame with vg': {skip: true},				//diffs
    'check frame after manual switch to frame with vg classic': {skip: true},			//diffs
    'check region by native selector': {skip: true},				                //Will be implement in separate task
    'check region by selector in frame in frame fully with scroll stitching': {skip: true},	//diffs
    'check hovered region by element with css stitching': {config: {branchName: 'current_python'}}, // diffs if compare to common baseline
    'check hovered region by element with scroll stitching': {skip: true},			//OutOfBoundsError: Region [Region(67, 0, 191 x 29, CONTEXT_RELATIVE)] is out of screenshot bounds [Region(0, 0, 685 x 460, SCREENSHOT_AS_IS)]
    'check region by selector in overflowed frame after manual scroll with css stitching': {skip: true},	//Stale element
    'check region by selector in overflowed frame after manual scroll with scroll stitching': {skip: true},	//Stale element
    'check regions by coordinates in frame with css stitching': {skip: true},		//Unable to locate element: {"method":"css selector","selector":"#modal2"}
    'check regions by coordinates in frame with scroll stitching': {skip: true},	//Unable to locate element: {"method":"css selector","selector":"#modal2"}
    'check regions by coordinates in frame with vg': {skip: true},			//diffs
    'should find regions by visual locator': {skip: true},				//Visual locators not implemented
    'should find regions by visual locator with vg': {skip: true},			//Visual locators not implemented
    'should not check if disabled': {skip: true},					//Unable to locate element: {"method":"css selector","selector":"[id="someId"]"}
    'should hide and restore scrollbars with scroll stitching': {skip: true},		//diff
    'should hide and restore scrollbars with vg': {skip: true},				// Unable to locate element: {"method":"css selector","selector":"#inner-frame-div"}
    'should send floating region by coordinates in frame with vg': {skip: true},	//diffs
    'should not send dom': {skip: true},						//diffs - info["actualAppOutput"][0]["image"]["hasDom"] == False,    assert True == False
    'should send dom on ie': {skip: true},						//diffs - assert info["actualAppOutput"][0]["image"]["hasDom"] == True   assert False == True
    'should send dom on edge legacy': {skip: true},					//eyes.open(driver)   -  EyesError: eyes.open_base() failed
    'should set viewport size on edge legacy': {skip: true},				//EyesError: Failed to set the viewport size
    'check window after manual scroll on safari 11': {skip: true},			//diffs
    'check window after manual scroll with vg': {skip: true},				//diffs
    'should send accessibility regions by selector with css stitching': {skip: true},		//Index error. [imageMatchSettings][accessibility] is empty...
    'should send accessibility regions by selector with scroll stitching': {skip: true},	//Index error. [imageMatchSettings][accessibility] is empty...
    'check window fully on android chrome emulator on desktop page': {skip: true},		//diffs
    'check window fully on android chrome emulator on mobile page with horizontal scroll': {skip: true},	//diffs
    'check window fully on android chrome emulator on mobile page': {skip: true},		//diffs
    'check window with layout breakpoints': {skip: true},				//layout breakpoints are not implemented
    'check window with layout breakpoints in config': {skip: true},			//layout breakpoints are not implemented
    'check window on page with sticky header with vg': {skip: true},			//diffs
    'check window fully with custom scroll root with css stitching': {skip: true},	//diffs
    'check window fully with fixed scroll root element': {config: {branchName: 'current_python'}}, // diffs if compare to common baseline
    'check scrollable modal region by selector fully with scroll stitching': {skip: true},	//diffs
    'check window fully and frame in frame fully with vg': {skip: true},		//diffs
    'check window fully on page with sticky header with scroll stitching': {skip: true},	//diffs
    'check scrollable modal region by selector fully with css stitching': {skip: true},		//diffs
    'check window fully and frame in frame fully with css stitching': {skip: true},		//diffs
    'check window fully and frame in frame fully with scroll stitching': {skip: true},		//diffs
    'check regions by coordinates in overflowed frame with vg': {skip: true},			//diffs
    'check region by selector fully with scroll stitching': {skip: true},			//diffs
    'check region in frame hidden under top bar fully with scroll stitching': {skip: true},	//diffs
    'check region in frame hidden under top bar fully with css stitching': {skip: true},	//diffs
    'check region by selector in frame fully with vg classic': {skip: true},			//Unable to locate element '#inner-frame-div'
    'check region by selector in frame fully with vg': {skip: true},				//Unable to locate element '#inner-frame-div'
    'check region by selector in frame fully with scroll stitching classic': {skip: true},	//diffs
    'check region by selector in frame fully with scroll stitching': {skip: true},		//diffs
    'check region by selector in overflowed frame fully with scroll stitching': {skip: true},	//diffs
    'check region by selector in overflowed frame fully with css stitching': {skip: true},	//diffs
    'check region fully after scroll non scrollable element with scroll stitching': {skip: true},	//diffs
    'check region by selector fully on page with sticky header with scroll stitching': {skip: true},	//diffs
    'check regions by coordinates in overflowed frame with scroll stitching': {skip: true},	// Unable to locate element: "#modal3"
    'check regions by coordinates in overflowed frame with css stitching': {skip: true},	// Unable to locate element: "#modal3"
    'check region by coordinates in frame fully with vg': {skip: true},				//diffs
    'check region by selector after manual scroll with scroll stitching': {skip: true},		//diffs
    'check region by selector after manual scroll with css stitching': {skip: true},		//diffs
    'check frame with scroll stitching classic': {skip: true},					//diffs
    'check frame with scroll stitching': {skip: true},						//diffs
    'check frame with css stitching classic': {skip: true},					//diffs
    'check frame with css stitching': {skip: true},						//diffs
    'check frame with vg classic': {skip: true},						//diffs
    'check frame with vg': {skip: true},							//diffs
    'check region by coordinates in frame with scroll stitching': {skip: true},			//diffs
    'check region by coordinates in frame with css stitching': {skip: true},			//diffs
    'check region by coordinates in frame with vg': {skip: true},				//diffs
    'check frame fully with css stitching': {skip: true},					//diffs
    'check frame in frame fully with scroll stitching': {skip: true},				//diffs
    'check frame in frame fully with css stitching': {skip: true},				//diffs
    'check frame in frame fully with vg': {skip: true},						//diffs
    'check frame fully with scroll stitching': {skip: true},					//diffs
    'check frame fully with vg': {skip: true},							//diffs
    'should send dom and location when check frame fully with vg': {skipEmit: true},
    'should send dom and location when check frame fully': {skipEmit: true},
    'should send dom and location when check frame': {skipEmit: true},
    'should send dom and location when check region by selector fully with custom scroll root': {skipEmit: true},
    'should send dom and location when check region by selector fully with vg': {skipEmit: true},
    'should send dom and location when check region by selector fully': {skipEmit: true},
    'should send dom and location when check region by selector in frame with vg': {skipEmit: true},
    'should send dom and location when check region by selector in frame': {skipEmit: true},
    'should send dom and location when check region by selector with custom scroll root with vg': {skipEmit: true},
    'should send dom and location when check region by selector with custom scroll root': {skipEmit: true},
    'should send dom and location when check region by selector with vg': {skipEmit: true},
    'should send dom and location when check region by selector': {skipEmit: true},
    'should send dom and location when check window fully with vg': {skipEmit: true},
    'should send dom and location when check window fully': {skipEmit: true},
    'should send dom and location when check window with vg': {skipEmit: true},
    'should send dom and location when check window': {skipEmit: true},
    'should send dom of version 11': {skipEmit: true},
    'appium android check window': {skip: true},						//assertion for ignored region fails
    'appium android check region with ignore region': {skip: true},				//assertion for ignored region fails
    'appium iOS check window': {skip: true},							//assertion for ignored region fails
    'appium iOS check region with ignore region': {skip: true},					//assertion for ignored region fails
    'appium iOS check region': {skip: true},							//wrong  scale
    'should not fail if scroll root is stale on android': {skipEmit: true},
    'check region by selector in frame fully on firefox legacy': { skipEmit: true },
    'should send custom batch properties': {skipEmit: true},
    'adopted styleSheets on chrome': {skipEmit: true},
	'adopted styleSheets on firefox': {skipEmit: true},
}
