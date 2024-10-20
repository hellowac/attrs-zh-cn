# mypy: ignore-errors
# SPDX-License-Identifier: MIT

"""
Commonly useful filters for `attrs.asdict` and `attrs.astuple`.
"""

from ._make import Attribute


def _split_what(what):
    """
    Returns a tuple of `frozenset`s of classes and attributes.
    """
    return (
        frozenset(cls for cls in what if isinstance(cls, type)),
        frozenset(cls for cls in what if isinstance(cls, str)),
        frozenset(cls for cls in what if isinstance(cls, Attribute)),
    )


def include(*what):
    """
    创建一个只允许 *what* 的过滤器。

    Args:
        what (list[type, str, attrs.Attribute]):
            要包含的内容。可以是类型、名称或属性。

    Returns:
        Callable:
            可传递给 `attrs.asdict` 和 `attrs.astuple` 的 *filter* 参数的可调用对象。

    .. versionchanged:: 23.1.0 接受字段名称的字符串。
    """
    cls, names, attrs = _split_what(what)

    def include_(attribute, value):
        return (
            value.__class__ in cls
            or attribute.name in names
            or attribute in attrs
        )

    return include_


def exclude(*what):
    """
    创建一个不允许 *what* 的过滤器。

    Args:
        what (list[type, str, attrs.Attribute]):
            要排除的内容. 可以是一个类型(type), 名称(name), 或者属性(attribute).

    Returns:
        Callable:
            A callable that can be passed to `attrs.asdict`'s and `attrs.astuple`'s *filter* argument.

            可以传递给 `attrs.asdict` 和 `attrs.astuple` 的 *filter* 参数的可调用函数。

    .. versionchanged:: 23.3.0 接受字段名称字符串作为输入参数
    """
    cls, names, attrs = _split_what(what)

    def exclude_(attribute, value):
        return not (
            value.__class__ in cls
            or attribute.name in names
            or attribute in attrs
        )

    return exclude_
