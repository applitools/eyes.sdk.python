from applitools.common.utils.general_utils import all_attrs, proxy_to


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


class TestObjInheritance(TestObj):
    def test_method2(self):
        return "test_method2"


def test_proxy_to():
    obj = TestObj()
    assert obj.test_method() == "test_method"
    assert obj.test_var == "test_var"
    assert obj.test_var_in_proxy == "test_var_in_proxy"
    assert obj.test_method_in_proxy() == "test_method_in_proxy"


def test_proxy_to_with_inheritance():
    obj2 = TestObjInheritance()
    assert obj2.test_method() == "test_method"
    assert obj2.test_var == "test_var"
    assert obj2.test_var_in_proxy == "test_var_in_proxy"
    assert obj2.test_method_in_proxy() == "test_method_in_proxy"
    assert obj2.test_method2() == "test_method2"
