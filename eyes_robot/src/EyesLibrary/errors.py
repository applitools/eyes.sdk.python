class EyesLibraryError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True


class EyesLibraryValueError(ValueError):
    ROBOT_EXIT_ON_FAILURE = True


class EyesLibraryConfigError(EyesLibraryValueError):
    pass
