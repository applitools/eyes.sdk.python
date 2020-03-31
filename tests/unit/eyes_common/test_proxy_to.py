from applitools.common.utils.general_utils import proxy_to, all_attrs


class ProxyToObj(object):
    def __init__(self):
        self.test_var_in_proxy = "test_var_in_proxy"

    def test_method_in_proxy(self):
        return "test_method_in_proxy"

    def _test_method_no_accessible(self):
        return "_test_method_no_accessible"


@proxy_to("some_obj")
class TestObj(object):
    def __init__(self):
        self.some_obj = ProxyToObj()
        self._proxy_to_fields = all_attrs(self.some_obj)
        self.test_var = "test_var"

    def test_method(self):
        return "test_method"


def test_proxy_to():
    obj = TestObj()
    assert obj.test_method() == "test_method"
    assert obj.test_var == "test_var"
    assert obj.test_var_in_proxy == "test_var_in_proxy"
    assert obj.test_method_in_proxy() == "test_method_in_proxy"
