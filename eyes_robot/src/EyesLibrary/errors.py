class EyesLibError(RuntimeError):
    pass


class EyesLibValueError(ValueError):
    pass


class EyesLibConfigParsingError(EyesLibValueError):
    pass
