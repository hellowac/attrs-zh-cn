# mypy: ignore-errors
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import ClassVar


class FrozenError(AttributeError):
    """
    尝试修改一个被 冻结/不可变(frozen/immutable) 的实例或属性。

    它的行为与 ``namedtuples`` 一致，使用相同的错误消息并继承自 `AttributeError`。

    .. versionadded:: 20.1.0
    """

    msg = "can't set attribute"
    args: ClassVar[tuple[str]] = [msg]


class FrozenInstanceError(FrozenError):
    """
    已尝试修改冻结(frozen)的实例。

    .. versionadded:: 16.1.0
    """


class FrozenAttributeError(FrozenError):
    """
    已尝试修改冻结(frozen)的属性。

    .. versionadded:: 20.1.0
    """


class AttrsAttributeNotFoundError(ValueError):
    """
    *attrs* 函数找不到用户要求的属性。

    .. versionadded:: 16.2.0
    """


class NotAnAttrsClassError(ValueError):
    """
    一个没有 *attrs* 的类已被传递到一个需要 *attrs* 的函数。

    .. versionadded:: 16.2.0
    """


class DefaultAlreadySetError(RuntimeError):
    """
    定义字段时已设置默认值，并尝试使用装饰器重置。

    .. versionadded:: 17.1.0
    """


class UnannotatedAttributeError(RuntimeError):
    """
    具有 ``auto_attribs=True`` 的类有一个没有类型注解的字段。

    .. versionadded:: 17.3.0
    """


class PythonTooOldError(RuntimeError):
    """
    尝试使用一个需要更高 Python 版本的 *attrs* 特性。

    .. versionadded:: 18.2.0
    """


class NotCallableError(TypeError):
    """
    需要可调用(callable)的字段(field)已被设置为不可调用的值。

    .. versionadded:: 19.2.0
    """

    def __init__(self, msg, value):
        super(TypeError, self).__init__(msg, value)
        self.msg = msg
        self.value = value

    def __str__(self):
        return str(self.msg)
