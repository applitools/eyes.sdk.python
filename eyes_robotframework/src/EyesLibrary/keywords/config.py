from __future__ import absolute_import, unicode_literals

from datetime import datetime
from typing import Any, Optional, Text, Union

from robot.api.deco import keyword
from six import string_types as basestring

from applitools.selenium import BatchInfo

from ..base import LibraryComponent


class ConfigurationKeywords(LibraryComponent):
    @keyword(
        "Create Batch Info",
        types={
            "name": str,
            "started_at": (datetime, str, None),
            "batch_sequence_name": (str, None),
            "batch_id": (str, None),
        },
    )
    def create_batch_info(
        self,
        name,  # type: Text
        started_at=None,  # type: Optional[Union[datetime,Text]]
        batch_sequence_name=None,  # type: Optional[Text]
        batch_id=None,  # type: Optional[Text]
    ):
        # type: (...) -> Text
        """
        Returns a BatchInfo ID string that may be used as batch argument on `Eyes Open`.

            | =Arguments=                  | =Description=                                                                              |
            | Name                         | The name of the batch                                                                      |
            | Started At                   | The date and time that will be displayed in the Test Manager as the batch start time *(*)* |
            | Batch ID                     | This argument groups together tests ran in different executions                            |

        The *Started At* argument may be passed as:
        - String: YYYY-mm-dd HH:MM:SS
        - Datetime variable: See [https://robotframework.org/robotframework/latest/libraries/DateTime.html|DateTime library]

        *Example:*
            | ${batch_id}= | Create Eyes Batch |
        """

        if started_at:
            if isinstance(started_at, basestring):
                started_at = datetime.strptime(started_at, "%Y-%m-%d %H:%M:%S")
            elif not isinstance(started_at, datetime):
                raise TypeError("BatchInfo started_at should be `str` or `datetime`")
        batch = BatchInfo(
            name, started_at=started_at, batch_sequence_name=batch_sequence_name
        )
        if batch_id:
            batch = batch.with_batch_id(batch_id)
        self.ctx.register_or_get_batch(batch)
        return batch.id

    @keyword("Get Eyes Configure Property", types=(str,))
    def get_eyes_configure_property(self, name):
        # type: (Text) -> Any
        return getattr(self.ctx.configure, name)

    @keyword("Set Eyes Configure Property", types=(str, str))
    def set_eyes_configure_property(self, name, value):
        # type: (Text, Any) -> Any
        setattr(self.ctx.configure, name, value)
