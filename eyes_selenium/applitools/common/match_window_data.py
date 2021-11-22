import typing

import attr

from .app_output import AppOutput
from .match import ImageMatchSettings
from .utils.json_utils import JsonInclude

if typing.TYPE_CHECKING:
    from typing import Optional, Text

    from .utils.custom_types import UserInputs


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
    :ivar source: App name or web page domain where checking is performed
    """

    name = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    user_inputs = attr.ib(metadata={JsonInclude.THIS: True})  # type: UserInputs
    replace_last = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    ignore_mismatch = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    ignore_match = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    force_mismatch = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    force_match = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    image_match_settings = attr.ib(
        type=ImageMatchSettings, metadata={JsonInclude.THIS: True}
    )  # type: ImageMatchSettings
    source = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Text]
    render_id = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Text]
    variant_id = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Text]


@attr.s
class MatchWindowData(object):
    """
    Encapsulates the data to be sent to the agent on a "match_window" command.

    :param user_inputs: A list of triggers between the previous
    matchWindow call and the current matchWindow call. Can be array of size 0,
    but MUST NOT be null.
    :param app_output: The appOutput for the current matchWindow call.
    :param tag: The tag of the window to be matched.
    :param ignore_mismatch: A flag indicating whether the server should ignore the image
     in case of a mismatch.
    :param options: A set of match options for the server.
    :param agent_setup: An object representing the configuration used to create the image.
    """

    # TODO Remove redundancy: user_inputs and ignore_mismatch should only be inside
    #  Options. (requires server version update).
    ignore_mismatch = attr.ib(metadata={JsonInclude.THIS: True})  # type: bool
    user_inputs = attr.ib(metadata={JsonInclude.THIS: True})  # type: UserInputs
    app_output = attr.ib(
        type=AppOutput, metadata={JsonInclude.THIS: True}
    )  # type: AppOutput
    tag = attr.ib(metadata={JsonInclude.THIS: True})  # type: Text
    options = attr.ib(type=Options, metadata={JsonInclude.THIS: True})  # type: Options
    agent_setup = attr.ib(metadata={JsonInclude.THIS: True})  # type: Optional[Text]
    render_id = attr.ib(metadata={JsonInclude.NON_NONE: True})  # type: Optional[Text]
