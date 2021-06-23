from ..base import LibraryComponent, keyword


class CheckKeywords(LibraryComponent):
    @keyword("Eyes Check")
    def check(self):
        ...

    @keyword("Eyes Check Window")
    def check_window(self):
        ...

    @keyword("Eyes Check Region")
    def check_region(self):
        ...


class TargetKeywords(LibraryComponent):
    @keyword("Eyes Target Window")
    def window(self):
        ...

    @keyword("Eyes Target Region")
    def region(self):
        ...

    @keyword("Eyes Target Frame")
    def frame(self):
        ...
