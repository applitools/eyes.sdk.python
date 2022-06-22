from applitools.eyes_universal import get_instance


def test_server_instance():
    instance = get_instance()

    assert isinstance(instance.port, int)
