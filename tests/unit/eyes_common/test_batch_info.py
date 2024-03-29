import os
from datetime import datetime

from mock import patch

from applitools.common.config import PROCESS_DEFAULT_BATCH_ID, BatchInfo


def test_create_batch_info(monkeypatch):
    now = datetime.now()
    batch_name = "Name"

    monkeypatch.delenv("APPLITOOLS_BATCH_ID")
    with patch("applitools.common.config.datetime") as mocked_datetime:
        mocked_datetime.now.return_value = now
        bi = BatchInfo(batch_name)
        bi.sequence_name = "sequence name"

    assert bi.name == batch_name
    assert bi.id == PROCESS_DEFAULT_BATCH_ID
    assert bi.started_at == now
    assert bi.sequence_name == "sequence name"


def test_create_two_batch_info_both_have_same_id(monkeypatch):
    monkeypatch.delenv("APPLITOOLS_BATCH_ID")
    bi1 = BatchInfo()
    bi2 = BatchInfo()

    assert bi1.id == PROCESS_DEFAULT_BATCH_ID
    assert bi2.id == PROCESS_DEFAULT_BATCH_ID


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


def test_set_batch_id_in_different_ways():
    raw_id = "2020-02-24T15:51:08.098515"
    bi = BatchInfo().with_batch_id(raw_id)
    assert bi.id == raw_id
    bi = BatchInfo()
    bi.id = raw_id
    assert bi.id == raw_id
    with patch.dict(os.environ, {"APPLITOOLS_BATCH_ID": "some id"}):
        bi = BatchInfo()
        assert bi.id == "some id"
