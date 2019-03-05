from datetime import datetime


def name_from_enum(e):
    # type: ignore
    #  # type: (Union[Enum, str]) -> str
    return e.name if hasattr(e, "name") else e


def isoformat(d):
    # type: (datetime) -> str
    return d.isoformat()


def round_converter(x):
    # type: (float) -> int
    return int(round(x))
