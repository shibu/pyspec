# -*- coding: ascii -*-

""" dbc - pyspec option module for design-by-contract support.

"""

#: This option controls pre post conditions
__pyspec_dbc_prepost_option = False
#: This option controls invariant conditions
__pyspec_dbc_invariant_option = False


def set_dbc_option(prepost=False, invariant=False):
    global __pyspec_dbc_prepost_option, __pyspec_dbc_invariant_option
    __pyspec_dbc_prepost_option = prepost
    __pyspec_dbc_invariant_option = invariant


def does_use_prepost():
    return __pyspec_dbc_prepost_option


def does_use_invariant():
    return __pyspec_dbc_invariant_option


def DbC(method):
    name = method.func_name
    if name.endswith("__pre") or name.endswith("__post") or \
           name == "__invariant":
       method.__pyspec_dbc_attribute = True
    return method


class DbCobject(object):
    def __init__(self):
        invariant_method = _get_invariant_method(self.__class__)
        if not hasattr(invariant_method, "__pyspec_dbc_attribute"):
            invarinat_method = None
        for name in dir(self):
            if not _is_valid_method_name(name):
                continue
            obj = getattr(self, name)
            if not callable(obj) or name in ("__class__"):
                continue
            pre = getattr(self, name+"__pre", None)
            if not hasattr(pre, "__pyspec_dbc_attribute"):
                pre = None
            post = getattr(self, name+"__post", None)
            if not hasattr(post, "__pyspec_dbc_attribute"):
                post = None
            proxy = _get_dbc_method_proxy(self, obj, pre, post, invariant_method)
            setattr(self, name, proxy)


def _is_valid_method_name(method_name):
    if method_name.endswith("__invariant") and method_name.startswith("_"):
        return False
    if method_name.endswith("__pre"):
        return False
    if method_name.endswith("__post"):
        return False
    return True


def _get_invariant_method(classobj):
    method_name = "_%s__invariant" % classobj.__name__
    return getattr(classobj, method_name, None)


def _call_invariant(obj):
    invariant_method = _get_invariant_method(obj.__class__)
    if invariant_method is not None:
        invariant_method(obj)
    for base in obj.__class__.__bases__:
        base_invariant = _get_invariant_method(base)
        if base_invariant is not None:
           base_invariant(obj)


def _get_dbc_method_proxy(obj, method, pre, post, invariant):
    if invariant is not None:
        if pre is not None and post is not None:
            def DbC_method_proxy111(*args, **kwargs):
                if __pyspec_dbc_prepost_option:
                    apply(pre, args, kwargs)
                    retval = apply(method, args, kwargs)
                    post(retval)
                    if __pyspec_dbc_invariant_option:
                       _call_invariant(obj)
                    return retval
                elif __pyspec_dbc_invariant_option:
                    retval = apply(method, args, kwargs)
                    _call_invariant(obj)
                    return retval
                return apply(method, args, kwargs)
            return DbC_method_proxy111
        elif pre is None and post is not None:
            def DbC_method_proxy011(*args, **kwargs):
                if __pyspec_dbc_prepost_option:
                    retval = apply(method, args, kwargs)
                    post(retval)
                    if __pyspec_dbc_invariant_option:
                       _call_invariant(obj)
                    return retval
                elif __pyspec_dbc_invariant_option:
                    retval = apply(method, args, kwargs)
                    _call_invariant(obj)
                    return retval
                return apply(method, args, kwargs)
            return DbC_method_proxy011
        elif pre is not None and post is None:
            def DbC_method_proxy101(*args, **kwargs):
                if __pyspec_dbc_prepost_option:
                    apply(pre, args, kwargs)
                    retval = apply(method, args, kwargs)
                    if __pyspec_dbc_invariant_option:
                       _call_invariant(obj)
                    return retval
                elif __pyspec_dbc_invariant_option:
                    retval = apply(method, args, kwargs)
                    _call_invariant(obj)
                    return retval
                return apply(method, args, kwargs)
            return DbC_method_proxy101
        else:
            def DbC_method_proxy001(*args, **kwargs):
                if __pyspec_dbc_invariant_option:
                    retval = apply(method, args, kwargs)
                    _call_invariant(obj)
                    return retval
                return apply(method, args, kwargs)
            return DbC_method_proxy001
    else:
        if pre is not None and post is not None:
            def DbC_method_proxy110(*args, **kwargs):
                if __pyspec_dbc_prepost_option:
                    apply(pre, args, kwargs)
                    retval = apply(method, args, kwargs)
                    post(retval)
                    return retval
                return apply(method, args, kwargs)
            return DbC_method_proxy110
        elif pre is None and post is not None:
            def DbC_method_proxy010(*args, **kwargs):
                if __pyspec_dbc_prepost_option:
                    retval = apply(method, args, kwargs)
                    post(retval)
                    return retval
                return apply(method, args, kwargs)
            return DbC_method_proxy010
        elif pre is not None and post is None:
            def DbC_method_proxy100(*args, **kwargs):
                if __pyspec_dbc_prepost_option:
                    apply(pre, args, kwargs)
                    retval = apply(method, args, kwargs)
                    return retval
                return apply(method, args, kwargs)
            return DbC_method_proxy100
        else:
            return method

