import os
import uuid
from datetime import datetime

from mock import patch

from applitools.common.config import BatchInfo


def test_create_batch_info(monkeypatch):
    uuid_value = str(uuid.uuid4())
    now = datetime.now()
    batch_name = "Name"

    monkeypatch.delenv("APPLITOOLS_BATCH_ID")
    with patch("uuid.uuid4") as mock_uuid:
        mock_uuid.return_value = uuid_value
        with patch(
            "applitools.common.config.configuration.datetime"
        ) as mocked_datetime:
            mocked_datetime.now.return_value = now
            bi = BatchInfo(batch_name)
            bi.sequence_name = "sequence name"

    assert bi.name == batch_name
    assert bi.id == uuid_value
    assert bi.started_at == now
    assert bi.sequence_name == "sequence name"


def test_create_batch_with_batch_id():
    bi = BatchInfo("My name").with_batch_id("custom id")
    assert bi.id == "custom id"


def test_set_env_params_in_batch_info():
    with patch.dict(
        os.environ,
        {
            "APPLITOOLS_BATCH_NAME": "name",
            "APPLITOOLS_BATCH_ID": "id",
            "APPLITOOLS_BATCH_SEQUENCE": "sequence name",
        },
    ):
        bi = BatchInfo()

    assert bi.name == "name"
    assert bi.id == "id"
    assert bi.sequence_name == "sequence name"


def test_get_set_id_in_batch_info():
    bi = BatchInfo()
    bi.id = "id_1"
    assert bi.id == "id_1"

    # backward compatibility
    bi.id_ = "id_2"
    assert bi.id == "id_2"
    assert bi.id_ == "id_2"
