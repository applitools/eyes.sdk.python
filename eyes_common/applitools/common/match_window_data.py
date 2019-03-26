import typing

import attr

from applitools.common.app_output import AppOutput
from applitools.common.match import ImageMatchSettings

if typing.TYPE_CHECKING:
    from typing import Text
    from applitools.common.utils.custom_types import UserInputs


__all__ = ("MatchWindowData", "Options")


@attr.s
class Options(object):
    """
    Encapsulates the "Options" section of the MatchExpectedOutput body data.

    :ivar name: The tag of the window to be matched.
    :ivar user_nputs: A list of triggers between the previous matchWindow call and
    the current matchWindow call. Can be array of size 0, but MUST NOT be null.
    :ivar ignore_mismatch: Tells the server whether or not to store a mismatch for
    the current window as window in the session.
    :ivar ignore_match: Tells the server whether or not to store a match for the
    current window as window in the session.
    :ivar force_mismatch: Forces the server to skip the comparison process and mark
    the current window as a mismatch.
    :ivar force_match: Forces the server to skip the comparison process and mark the
    current window as a match.
    :ivar image_match_settings
    """

    name = attr.ib()  # type: Text
    user_inputs = attr.ib()  # type: UserInputs
    ignore_mismatch = attr.ib()  # type: bool
    ignore_match = attr.ib()  # type: bool
    force_mismatch = attr.ib()  # type: bool
    force_match = attr.ib()  # type: bool
    image_match_settings = attr.ib(type=ImageMatchSettings)  # type: ImageMatchSettings


@attr.s
class MatchWindowData(object):
    """
    Encapsulates the data to be sent to the agent on a "matchWindow" command.

    :param user_inputs: A list of triggers between the previous
    matchWindow call and the current matchWindow call. Can be array of size 0,
    but MUST NOT be null.
    :param app_output: The appOutput for the current matchWindow call.
    :param tag: The tag of the window to be matched.
    :param ignore_mismatch: A flag indicating whether the server should ignore the image in case of a mismatch.
    :param options: A set of match options for the server.
    :param agent_setup: An object representing the configuration used to create the image.
    """

    #  TODO Remove redundancy: userInputs and ignoreMismatch should only be inside Options. (requires server version update).
    ignore_mismatch = attr.ib()  # type: bool
    user_inputs = attr.ib()  # type: UserInputs
    app_output = attr.ib(type=AppOutput)  # type: AppOutput
    tag = attr.ib()  # type: Text
    options = attr.ib()  # type: Options
    agent_setup = attr.ib()  # type: Text
