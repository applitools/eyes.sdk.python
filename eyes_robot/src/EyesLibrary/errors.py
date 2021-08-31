class EyesLibraryError(RuntimeError):
    pass


class EyesLibraryValueError(ValueError):
    pass


class EyesLibraryConfigError(EyesLibraryValueError):
    pass
