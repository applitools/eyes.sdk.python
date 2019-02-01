import typing as tp

from .errors import EyesError

__all__ = ("MatchLevel", "ExactMatchSettings", "ImageMatchSettings")


class MatchLevel(object):
    """
    The extent in which two images match (or are expected to match).
    """

    NONE = "None"
    LEGACY_LAYOUT = "Layout1"
    LAYOUT = "Layout2"
    LAYOUT2 = "Layout2"
    CONTENT = "Content"
    STRICT = "Strict"
    EXACT = "Exact"


class ExactMatchSettings(object):
    """
    Encapsulates settings for the "Exact" match level.
    """

    def __init__(
        self,
        min_diff_intensity=0,
        min_diff_width=0,
        min_diff_height=0,
        match_threshold=0.0,
    ):
        # type: (int, int, int, float) -> None
        """
        Ctor.

        :param min_diff_intensity: Minimal non-ignorable pixel intensity difference.
        :param min_diff_width: Minimal non-ignorable diff region width.
        :param min_diff_height: Minimal non-ignorable diff region height.
        :param match_threshold: The ratio of differing pixels above which images
                                are considered mismatching.
        """
        self.min_diff_intensity = min_diff_intensity  # type: int
        self.min_diff_width = min_diff_width  # type: int
        self.min_diff_height = min_diff_height  # type: int
        self.match_threshold = match_threshold  # type: float

    def __getstate__(self):
        return dict(
            minDiffIntensity=self.min_diff_intensity,
            minDiffWidth=self.min_diff_width,
            minDiffHeight=self.min_diff_height,
            matchThreshold=self.match_threshold,
        )

    # This is required in order for jsonpickle to work on this object.
    # noinspection PyMethodMayBeStatic
    def __setstate__(self, state):
        raise EyesError("Cannot create ExactMatchSettings instance from dict!")

    def __str__(self):
        return (
            "[min diff intensity: %d, min diff width: %d, min diff height: %d,"
            " match threshold: %f]"
            % (
                self.min_diff_intensity,
                self.min_diff_width,
                self.min_diff_height,
                self.match_threshold,
            )
        )


class ImageMatchSettings(object):
    """
    Encapsulates match settings for the a session.
    """

    def __init__(self, match_level=MatchLevel.STRICT, exact_settings=None):
        # type: (tp.Text, tp.Optional[ExactMatchSettings]) -> None
        """
        :param match_level: The "strictness" level of the match.
        :param exact_settings: Parameter for fine tuning the match
                               when "Exact" match level is used.
        """
        self.match_level = match_level  # type: tp.Text
        self.exact_settings = exact_settings  # type: tp.Optional[ExactMatchSettings]

    def __getstate__(self):
        return dict(matchLevel=self.match_level, exact=self.exact_settings)

    # This is required in order for jsonpickle to work on this object.
    # noinspection PyMethodMayBeStatic
    def __setstate__(self, state):
        raise EyesError("Cannot create ImageMatchSettings instance from dict!")

    def __str__(self):
        return "[Match level: %s, Exact match settings: %s]" % (
            self.match_level,
            self.exact_settings,
        )
