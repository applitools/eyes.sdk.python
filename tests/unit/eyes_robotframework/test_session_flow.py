from mock import Mock, patch

from EyesLibrary.keywords import session


def test_assign_batch_info_to_eyes_open(session_keyword, configuration_keyword):
    batch_id = configuration_keyword.create_batch_info(name="Batch Name")
    with patch.object(session, "Eyes", return_value=Mock()):
        session_keyword.open(test_name="Test", app_name="TEST", batch=batch_id)
    assert session_keyword.ctx.configure.batch.id == batch_id
