# -*- coding: ascii -*-

__pyspec = 1
from embedded.setting import config
from util import create_method_repr


class TestProxy(object):
    def __init__(self, target_object, runtime_option, check_return,
                 check_args=True):
        super(TestProxy, self).__init__(target_object, runtime_option)
        self._target_object = target_object
        if runtime_option is None:
            runtime_option = config.runtime
        records, changed = runtime_option.get_recorded_value(
                                self.__class__.__name__, [])
        self._check_return = check_return
        self._check_args = check_args
        if changed:
            self._legacy_object_record = records
            self._recording_mode = True
            runtime_option.recording_flag = True
        else:
            self._legacy_object_record = records[:]
            self._recording_mode = False

    def __getattribute__(self, name):
        try:
            return super(TestProxy, self).__getattribute__(name)
        except AttributeError:
            return getattr(self._target_object, name)

    def _dump_args(self, args, kwargs):
        str_args = [str(arg) for arg in args]
        str_kwargs = [(key, str(value)) for key, value in kwargs.iteritems()]
        str_kwargs.sort()
        return str_args, str_kwargs

    def _record_method_call(self, name, args, kwargs, result):
        method_repr = create_method_repr(name, args, kwargs)
        if self._recording_mode:
            if self._check_return:
                print "recording: %s => %s" % (method_repr, result)
            else:
                print "recording: %s" % method_repr
            if self._check_args:
                if self._check_return:
                    self._legacy_object_record.append(
                            (name, self._dump_args(args, kwargs), result))
                else:
                    self._legacy_object_record.append(
                            (name, self._dump_args(args, kwargs), None))
            else:
                if self._check_return:
                    self._legacy_object_record.append(
                            (name, None, None, result))
                else:
                    self._legacy_object_record.append(
                            (name, None, None, None))
        else:
            if len(self._legacy_object_record) == 0:
                raise AssertionError("Unexpected method was called: %s"
                        % method_repr)
            record = self._legacy_object_record[0]
            del self._legacy_object_record[0]
            if name != record[0]:
                raise AssertionError("Unexpected method was called: %s"
                        % method_repr)
            if self._check_args:
                str_args = self._dump_args(args, kwargs)
                if str_args != record[1]:
                    expected = create_method_repr(name, record[1][0],
                            dict(record[1][1]))
                    raise AssertionError(
                        "Argument value of %s() was changed: %s => %s" %
                            (name, method_repr, expected))
            if self._check_return:
                if result != record[2]:
                    raise AssertionError(
                             "Return value of %s was changed: %s => %s" %
                             (method_repr, record[2], result))


def make_binder(unbound_method):
    def proxy(self, *args, **kwargs):
        result = unbound_method(self._target_object, *args, **kwargs)
        self._record_method_call(unbound_method.__name__, args, kwargs, result)
        return result
    proxy.__name__ = unbound_method.__name__
    return proxy


_proxy_classes = {}


def test_proxy(target_object, hook_methods=[], runtime_option=None,
        check_return=True, check_args=True):
    obj_cls = target_object.__class__
    key = (obj_cls, tuple(hook_methods))
    cls = _proxy_classes.get(key)
    if cls is None:
        cls = type("%sProxy" % obj_cls.__name__, (TestProxy,), {})
        if len(hook_methods) == 0:
            hook_methods = []
            for attribute in dir(target_object):
                if attribute in ("__init__", "__getattribute__",
                                 "__setattr__", "__hash__",
                                 "__delattr__", "__new__", "__class__"):
                    continue
                if callable(getattr(target_object, attribute)):
                    hook_methods.append(attribute)
        #print hook_methods
        for hook_method in hook_methods:
            unbound_method = getattr(obj_cls, hook_method)
            setattr(cls, hook_method, make_binder(unbound_method))
        _proxy_classes[key] = cls
    return cls(target_object, runtime_option, check_return)
