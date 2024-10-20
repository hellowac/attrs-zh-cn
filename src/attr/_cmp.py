# mypy: ignore-errors
# SPDX-License-Identifier: MIT


import functools
import types

from ._make import _make_ne


_operation_names = {"eq": "==", "lt": "<", "le": "<=", "gt": ">", "ge": ">="}


def cmp_using(
    eq=None,
    lt=None,
    le=None,
    gt=None,
    ge=None,
    require_same_type=True,
    class_name="Comparable",
):
    """
    创建一个可以传递给 `attrs.field` 的 ``eq``, ``order`` 和 ``cmp`` 参数以自定义字段比较的类。

    如果提供了至少一个 ``{lt, le, gt, ge}`` 和 ``eq`` ，生成的类将具有完整的排序方法。

    Args:
        eq (typing.Callable | None):
            用于评估两个对象相等性的可调用对象。

        lt (typing.Callable | None):
            用于评估一个对象是否小于另一个对象的可调用对象。

        le (typing.Callable | None):
            用于评估一个对象是否小于或等于另一个对象的可调用对象。

        gt (typing.Callable | None):
            用于评估一个对象是否大于另一个对象的可调用对象。

        ge (typing.Callable | None):
            用于评估一个对象是否大于或等于另一个对象的可调用对象。

        require_same_type (bool):
            当为 `True` 时，如果对象不是同一类型，则相等和排序方法将返回 `NotImplemented`。

        class_name (str | None): 类的名称。默认为 "Comparable"。

    有关更多详细信息，请参阅 `comparison` 。

    .. versionadded:: 21.1.0
    """

    body = {
        "__slots__": ["value"],
        "__init__": _make_init(),
        "_requirements": [],
        "_is_comparable_to": _is_comparable_to,
    }

    # Add operations.
    num_order_functions = 0
    has_eq_function = False

    if eq is not None:
        has_eq_function = True
        body["__eq__"] = _make_operator("eq", eq)
        body["__ne__"] = _make_ne()

    if lt is not None:
        num_order_functions += 1
        body["__lt__"] = _make_operator("lt", lt)

    if le is not None:
        num_order_functions += 1
        body["__le__"] = _make_operator("le", le)

    if gt is not None:
        num_order_functions += 1
        body["__gt__"] = _make_operator("gt", gt)

    if ge is not None:
        num_order_functions += 1
        body["__ge__"] = _make_operator("ge", ge)

    type_ = types.new_class(
        class_name, (object,), {}, lambda ns: ns.update(body)
    )

    # Add same type requirement.
    if require_same_type:
        type_._requirements.append(_check_same_type)

    # Add total ordering if at least one operation was defined.
    if 0 < num_order_functions < 4:
        if not has_eq_function:
            # functools.total_ordering requires __eq__ to be defined,
            # so raise early error here to keep a nice stack.
            msg = "eq must be define is order to complete ordering from lt, le, gt, ge."
            raise ValueError(msg)
        type_ = functools.total_ordering(type_)

    return type_


def _make_init():
    """
    Create __init__ method.
    """

    def __init__(self, value):
        """
        Initialize object with *value*.
        """
        self.value = value

    return __init__


def _make_operator(name, func):
    """
    Create operator method.
    """

    def method(self, other):
        if not self._is_comparable_to(other):
            return NotImplemented

        result = func(self.value, other.value)
        if result is NotImplemented:
            return NotImplemented

        return result

    method.__name__ = f"__{name}__"
    method.__doc__ = (
        f"Return a {_operation_names[name]} b.  Computed by attrs."
    )

    return method


def _is_comparable_to(self, other):
    """
    Check whether `other` is comparable to `self`.
    """
    return all(func(self, other) for func in self._requirements)


def _check_same_type(self, other):
    """
    Return True if *self* and *other* are of the same type, False otherwise.
    """
    return other.value.__class__ is self.value.__class__
