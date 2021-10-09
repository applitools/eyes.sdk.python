def test_create_batch_info(configuration_keyword):
    batch_id = configuration_keyword.create_batch_info(
        name="Batch Name", batch_sequence_name="Sequence Name"
    )
    batch = configuration_keyword.ctx._batch_registry[batch_id]
    assert batch.name == "Batch Name"
    assert batch.id == batch_id
    assert batch.sequence_name == "Sequence Name"
