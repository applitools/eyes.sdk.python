from enum import Enum


class SessionType(Enum):
    # default type of sessions.
    SEQUENTIAL = "SEQUENTIAL"
    # a timing test session
    PROGRESSION = "PROGRESSION"
