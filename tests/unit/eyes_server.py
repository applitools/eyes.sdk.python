from applitools.eyes_server import get_instance


def test_server_instance():
    instance = get_instance()

    assert instance.port == 2107
