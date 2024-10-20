# mypy: ignore-errors
# SPDX-License-Identifier: MIT

"""
Commonly useful converters.
"""

import typing

from ._compat import _AnnotationExtractor
from ._make import NOTHING, Factory, pipe


__all__ = [
    "default_if_none",
    "optional",
    "pipe",
    "to_bool",
]


def optional(converter):
    """
    一个允许属性可选的转换器。可选属性
    可以设置为 `None`。

    如果包装的转换器有类型注解，将会被推断出来。

    Args:
        converter (typing.Callable):
            用于非 `None` 值的转换器。

    .. versionadded:: 17.1.0
    """

    def optional_converter(val):
        if val is None:
            return None
        return converter(val)

    xtr = _AnnotationExtractor(converter)

    t = xtr.get_first_param_type()
    if t:
        optional_converter.__annotations__["val"] = typing.Optional[t]

    rt = xtr.get_return_type()
    if rt:
        optional_converter.__annotations__["return"] = typing.Optional[rt]

    return optional_converter


def default_if_none(default=NOTHING, factory=None):
    """
    一个允许将 `None` 值替换为 *default* 或 *factory* 结果的转换器。

    Args:
        default:
            如果传入 `None`，将使用的值。支持传入 `attrs.Factory` 的实例，
            但是不支持 ``takes_self`` 选项。

        factory (typing.Callable):
            一个不带参数的可调用，其结果将在传入 `None` 时使用。

    Raises:
        TypeError: 如果 **既没有** 传入 *default* 也没有 *factory*。

        TypeError: 如果 **同时** 传入 *default* 和 *factory*。

        ValueError:
            如果传入 `attrs.Factory` 的实例且
            ``takes_self=True``。

    .. versionadded:: 18.2.0
    """
    if default is NOTHING and factory is None:
        msg = "Must pass either `default` or `factory`."
        raise TypeError(msg)

    if default is not NOTHING and factory is not None:
        msg = "Must pass either `default` or `factory` but not both."
        raise TypeError(msg)

    if factory is not None:
        default = Factory(factory)

    if isinstance(default, Factory):
        if default.takes_self:
            msg = "`takes_self` is not supported by default_if_none."
            raise ValueError(msg)

        def default_if_none_converter(val):
            if val is not None:
                return val

            return default.factory()

    else:

        def default_if_none_converter(val):
            if val is not None:
                return val

            return default

    return default_if_none_converter


def to_bool(val):
    """
    将“布尔”字符串（例如，来自环境变量）转换为真实的布尔值。

    映射为 `True` 的值：

    - ``True``
    - ``"true"`` / ``"t"``
    - ``"yes"`` / ``"y"``
    - ``"on"``
    - ``"1"``
    - ``1``

    映射为 `False` 的值：

    - ``False``
    - ``"false"`` / ``"f"``
    - ``"no"`` / ``"n"``
    - ``"off"``
    - ``"0"``
    - ``0``

    Raises:
        ValueError: 对于任何其他值。

    .. versionadded:: 21.3.0
    """
    if isinstance(val, str):
        val = val.lower()

    if val in (True, "true", "t", "yes", "y", "on", "1", 1):
        return True
    if val in (False, "false", "f", "no", "n", "off", "0", 0):
        return False

    msg = f"Cannot convert value to bool: {val!r}"
    raise ValueError(msg)
