module.exports = {
    "css": (selector) => `[By.CSS_SELECTOR, ${selector}]`,
    "class name": (selector) => `[By.CLASS_NAME, ${selector}]`,
    "id": (selector) => `[By.ID, ${selector}]`,
    "accessibility id": (selector) => `[MobileBy.ACCESSIBILITY_ID, (${selector})]`,
    "-android uiautomator": (selector) => `[MobileBy.ANDROID_UIAUTOMATOR, (${selector})]`,
    "androidViewTag": (selector) => `[MobileBy.ANDROID_VIEWTAG, (${selector})]`,
    "-ios predicate string": (selector) => `[MobileBy.IOS_PREDICATE, (${selector})]`,
    "-ios class chain": (selector) => `[MobileBy.IOS_CLASS_CHAIN, (${selector})]`,
}
