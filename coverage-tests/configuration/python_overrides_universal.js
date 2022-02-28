module.exports = {
    // fails in selenium4 only due to legacy driver being used
    'check window after manual scroll on safari 11': {skip: true},

    // Shadow emitter not implemented
    'check region by element within shadow dom with vg': {skip: true},

    // Stale element are not handled by python binding
    'should handle check of stale element if selector is preserved': {skip: true},
    'should handle check of stale element in frame if selector is preserved': {skip: true},

    // Failing on the universal server 1.10 and lower
    // check on new universal server version
    "check window on mobile web android": {skip: true}

}
