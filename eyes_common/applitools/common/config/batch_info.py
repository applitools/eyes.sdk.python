import os
import uuid
from datetime import datetime
from typing import Optional, Text

from applitools.common.errors import EyesError
from applitools.common.utils import general_utils


class BatchInfo(object):
    """
    A batch of tests.
    """

    def __init__(self, name=None, started_at=None):
        # type: (Optional[Text], Optional[datetime]) -> None
        if started_at is None:
            started_at = datetime.now(general_utils.UTC)

        self.name = (
            name if name else os.environ.get("APPLITOOLS_BATCH_NAME", None)
        )  # type: Optional[Text]
        self.started_at = started_at  # type: datetime
        self.id = os.environ.get("APPLITOOLS_BATCH_ID", str(uuid.uuid4()))  # type: Text

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
        raise EyesError("Cannot create BatchInfo instance from dict!")

    def __repr__(self):
        return "%s - %s - %s" % (self.name, self.started_at, self.id)
