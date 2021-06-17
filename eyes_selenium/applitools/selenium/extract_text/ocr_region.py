from applitools.core import BaseOCRRegion


class OCRRegion(BaseOCRRegion):
    def __init__(self, target):
        # type:(Union[Region,CssSelector,AnyWebElement])->None
        super(OCRRegion, self).__init__(target)
        self.process_app_output = None  # type: Optional[Callable]
        self.app_output_with_screenshot = (
            None
        )  # type: Optional[AppOutputWithScreenshot]

    def add_process_app_output(self, callback):
        # type: (Callable) -> None
        if not callable(callback):
            raise ValueError
        self.process_app_output = callback
