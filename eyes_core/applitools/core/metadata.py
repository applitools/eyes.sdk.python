import uuid
import os
import typing as tp
from datetime import datetime

from .errors import EyesError
from .utils import general_utils


class BatchInfo(object):
    """
    A batch of tests.
    """

    def __init__(self, name=None, started_at=None):
        # type: (tp.Optional[tp.Text], tp.Optional[datetime]) -> None
        if started_at is None:
            started_at = datetime.now(general_utils.UTC)

        self.name = name if name else os.environ.get('APPLITOOLS_BATCH_NAME', None)  # type: tp.Optional[tp.Text]
        self.started_at = started_at  # type: datetime
        self.id = os.environ.get('APPLITOOLS_BATCH_ID', str(uuid.uuid4()))  # type: tp.Text

    @property
    def id_(self):
        # TODO: Remove in this way of initialization in future
        return self.id

    @id_.setter
    def id_(self, value):
        self.id = value

    def __getstate__(self):
        return dict(name=self.name, startedAt=self.started_at.isoformat(), id=self.id)

    # Required is required in order for jsonpickle to work on this object.
    # noinspection PyMethodMayBeStatic
    def __setstate__(self, state):
        raise EyesError('Cannot create BatchInfo instance from dict!')

    def __str__(self):
        return "%s - %s - %s" % (self.name, self.started_at, self.id)


class CoordinatesType(object):
    """
     Encapsulates the type of coordinates used by the region provider.
    """

    # The coordinates should be used "as is" on the screenshot image.
    # Regardless of the current context.
    SCREENSHOT_AS_IS = 'SCREENSHOT_AS_IS'

    # The coordinates should be used "as is" within the current context. For
    # example, if we're inside a frame, the coordinates are "as is",
    # but within the current frame's viewport.
    CONTEXT_AS_IS = 'CONTEXT_AS_IS'

    # Coordinates are relative to the context. For example, if we are in
    # a context of a frame in a web page, then the coordinates are relative to
    # the  frame. In this case, if we want to crop an image region based on
    # an element's region, we will need to calculate their respective "as
    # is" coordinates.
    CONTEXT_RELATIVE = 'CONTEXT_RELATIVE'
