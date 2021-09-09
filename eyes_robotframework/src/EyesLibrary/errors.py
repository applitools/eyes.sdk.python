class EyesLibraryError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True


class EyesLibraryValueError(ValueError):
    pass


class EyesLibraryConfigError(EyesLibraryValueError):
    ROBOT_EXIT_ON_FAILURE = True
    pass
