from applitools.common.utils import ABC
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


def test_proxy_to_simple_case():
    obj = TestObj()
    assert obj.test_method() == "test_method"
    assert obj.test_var == "test_var"
    assert obj.test_var_in_proxy == "test_var_in_proxy"
    assert obj.test_method_in_proxy() == "test_method_in_proxy"


class TestObjInherited(TestObj):
    def test_method2(self):
        return "test_method2"


def test_base_class_decorated_with_proxy_to_and_check_inherited():
    obj = TestObjInherited()
    assert obj.test_method() == "test_method"
    assert obj.test_var == "test_var"
    assert obj.test_var_in_proxy == "test_var_in_proxy"
    assert obj.test_method_in_proxy() == "test_method_in_proxy"
    assert obj.test_method2() == "test_method2"


class FirstClass(ABC):
    def test_method2(self):
        return "test_method2"


class SecondCLass(object):
    def __init__(self):
        self.setting_some_attr = "setting_some_attr"
        self._some_obj = ProxyToObj()

    @property
    def some_obj(self):
        return self._some_obj


@proxy_to("some_obj")
class LastClass(FirstClass, SecondCLass):
    def __init__(self):
        super(LastClass, self).__init__()
        self._proxy_to_fields = all_attrs(self.some_obj)
        self.test_var = "test_var"

    def test_method(self):
        return "test_method"


def test_decorated_class_with_multiple_inheritance():
    obj = LastClass()
    assert obj.test_method() == "test_method"
    assert obj.test_var == "test_var"
    assert obj.test_var_in_proxy == "test_var_in_proxy"
    assert obj.test_method_in_proxy() == "test_method_in_proxy"
    assert obj.test_method2() == "test_method2"
    assert obj.setting_some_attr == "setting_some_attr"
