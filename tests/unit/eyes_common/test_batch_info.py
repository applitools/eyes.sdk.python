import json
import os
import uuid
from datetime import datetime

from applitools.common.config import BatchInfo
from mock import patch

from applitools.common.utils import json_utils


def test_create_batch_info(monkeypatch):
    uuid_value = str(uuid.uuid4())
    now = datetime.now()
    batch_name = "Name"

    monkeypatch.delenv("APPLITOOLS_BATCH_ID")
    with patch("uuid.uuid4") as mock_uuid:
        mock_uuid.return_value = uuid_value
        with patch("applitools.common.config.datetime") as mocked_datetime:
            mocked_datetime.now.return_value = now
            bi = BatchInfo(batch_name)
            bi.sequence_name = "sequence name"

    assert bi.name == batch_name
    assert bi.id == uuid_value
    assert bi.started_at == now
    assert bi.sequence_name == "sequence name"


def test_batch_info_with_date():
    now = datetime.now()
    bi = BatchInfo(None, now)
    assert bi.started_at == now


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
            "APPLITOOLS_BATCH_NOTIFY": "true",
        },
    ):
        bi = BatchInfo()

    assert bi.name == "name"
    assert bi.id == "id"
    assert bi.sequence_name == "sequence name"
    assert bi.notify_on_completion == True


def test_encode_id_field():
    raw_id = "2020-02-24T15:51:08.098515"
    encoded_id = "2020-02-24T15%3A51%3A08.098515"
    bi = BatchInfo().with_batch_id(raw_id)
    assert bi.id == encoded_id
    bi = BatchInfo()
    bi.id = raw_id
    assert bi.id == encoded_id


def test_serialization_of_batch_info():
    bi = BatchInfo(name="Name", batch_sequence_name="BatchName").with_batch_id(
        "custom-id"
    )
    res = json.loads(json_utils.to_json(bi))
    print(res)
    assert res["name"] == "Name"
    assert res["batchSequenceName"] == "BatchName"
    assert res["notifyOnCompletion"] == False
    assert res["id"] == "custom-id"
