# mypy: ignore-errors
# SPDX-License-Identifier: MIT

"""
Commonly useful validators.
"""

import operator
import re

from contextlib import contextmanager
from re import Pattern

from ._config import get_run_validators, set_run_validators
from ._make import _AndValidator, and_, attrib, attrs
from .converters import default_if_none
from .exceptions import NotCallableError


__all__ = [
    "and_",
    "deep_iterable",
    "deep_mapping",
    "disabled",
    "ge",
    "get_disabled",
    "gt",
    "in_",
    "instance_of",
    "is_callable",
    "le",
    "lt",
    "matches_re",
    "max_len",
    "min_len",
    "not_",
    "optional",
    "or_",
    "set_disabled",
]


def set_disabled(disabled):
    """
    全局禁用或启用运行验证器。

    默认情况下，它们是运行的。

    Args:
        disabled (bool): 如果为 `True`，禁用运行所有验证器。

    .. warning::

        此函数不是线程安全的！

    .. versionadded:: 21.3.0
    """
    set_run_validators(not disabled)


def get_disabled():
    """
    返回一个布尔值，指示验证器当前是否被禁用。

    Returns:
        bool: 如果验证器当前被禁用，则返回 `True`。

    .. versionadded:: 21.3.0
    """
    return not get_run_validators()


@contextmanager
def disabled():
    """
    上下文管理器，在其上下文中禁用运行验证器。

    .. warning::

        此上下文管理器不是线程安全的！

    .. versionadded:: 21.3.0
    """
    set_run_validators(False)
    try:
        yield
    finally:
        set_run_validators(True)


@attrs(repr=False, slots=True, unsafe_hash=True)
class _InstanceOfValidator:
    type = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not isinstance(value, self.type):
            msg = f"'{attr.name}' must be {self.type!r} (got {value!r} that is a {value.__class__!r})."
            raise TypeError(
                msg,
                attr,
                self.type,
                value,
            )

    def __repr__(self):
        return f"<instance_of validator for type {self.type!r}>"


def instance_of(type):
    """
    一个验证器，如果初始化器使用错误类型调用该特定属性，则引发 `TypeError` 
    （检查使用 `isinstance` 执行，因此也可以传递类型元组）。

    Args:
        type (type | tuple[type]): 要检查的类型。

    Raises:
        TypeError:
            带有人类可读的错误消息，属性（类型为 `attrs.Attribute` ）、预期类型和它接收到的值。
    """
    return _InstanceOfValidator(type)


@attrs(repr=False, frozen=True, slots=True)
class _MatchesReValidator:
    pattern = attrib()
    match_func = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not self.match_func(value):
            msg = f"'{attr.name}' must match regex {self.pattern.pattern!r} ({value!r} doesn't)"
            raise ValueError(
                msg,
                attr,
                self.pattern,
                value,
            )

    def __repr__(self):
        return f"<matches_re validator for pattern {self.pattern!r}>"


def matches_re(regex, flags=0, func=None):
    r"""
    一个验证器，如果初始化器被调用时提供的字符串不匹配 *regex*，
    则会引发 `ValueError` 。

    Args:
        regex (str, re.Pattern):
            一个正则表达式字符串或预编译模式，用于匹配

        flags (int):
            将传递给底层 re 函数的标志（默认为 0）

        func (typing.Callable):
            调用哪个底层 `re` 函数。有效选项为
            `re.fullmatch`、`re.search` 和 `re.match`；默认值为 `None`
            意味着使用 `re.fullmatch`。出于性能考虑，模式总是使用
            `re.compile` 预编译。

    .. versionadded:: 19.2.0
    .. versionchanged:: 21.3.0 *regex* 可以是预编译模式。
    """
    valid_funcs = (re.fullmatch, None, re.search, re.match)
    if func not in valid_funcs:
        msg = "'func' must be one of {}.".format(
            ", ".join(
                sorted(e and e.__name__ or "None" for e in set(valid_funcs))
            )
        )
        raise ValueError(msg)

    if isinstance(regex, Pattern):
        if flags:
            msg = "'flags' can only be used with a string pattern; pass flags to re.compile() instead"
            raise TypeError(msg)
        pattern = regex
    else:
        pattern = re.compile(regex, flags)

    if func is re.match:
        match_func = pattern.match
    elif func is re.search:
        match_func = pattern.search
    else:
        match_func = pattern.fullmatch

    return _MatchesReValidator(pattern, match_func)


@attrs(repr=False, slots=True, unsafe_hash=True)
class _OptionalValidator:
    validator = attrib()

    def __call__(self, inst, attr, value):
        if value is None:
            return

        self.validator(inst, attr, value)

    def __repr__(self):
        return f"<optional validator for {self.validator!r} or None>"


def optional(validator):
    """
    一个使属性可选的验证器。可选属性是指可以设置为 `None` ，并且满足
    子验证器的要求。

    Args:
        validator
            (typing.Callable | tuple[typing.Callable] | list[typing.Callable]):
            用于非 `None` 值的验证器（或验证器列表）。

    .. versionadded:: 15.1.0
    .. versionchanged:: 17.1.0 *validator* 可以是验证器列表。
    .. versionchanged:: 23.1.0 *validator* 也可以是验证器元组。
    """
    if isinstance(validator, (list, tuple)):
        return _OptionalValidator(_AndValidator(validator))

    return _OptionalValidator(validator)


@attrs(repr=False, slots=True, unsafe_hash=True)
class _InValidator:
    options = attrib()
    _original_options = attrib(hash=False)

    def __call__(self, inst, attr, value):
        try:
            in_options = value in self.options
        except TypeError:  # e.g. `1 in "abc"`
            in_options = False

        if not in_options:
            msg = f"'{attr.name}' must be in {self._original_options!r} (got {value!r})"
            raise ValueError(
                msg,
                attr,
                self._original_options,
                value,
            )

    def __repr__(self):
        return f"<in_ validator with options {self._original_options!r}>"


def in_(options):
    """
    一个验证器，如果初始化器使用不在提供的 *options* 中的值调用，则引发 `ValueError`。

    检查使用 ``value in options`` 执行，因此 *options* 必须支持该操作。

    为了保持验证器的可哈希性，字典、列表和集合会透明地转换为 `tuple`。

    Args:
        options: 允许的选项。

    Raises:
        ValueError:
            带有人类可读的错误消息，属性（类型为 `attrs.Attribute`）、预期选项和它接收到的值。

    .. versionadded:: 17.1.0
    .. versionchanged:: 22.1.0
       直到现在，ValueError 还不完整，仅包含人类可读的错误消息。现在它包含自 17.1.0 以来承诺的所有信息。
    .. versionchanged:: 24.1.0
       现在，作为列表、字典或集合的 *options* 被转换为元组，以保持验证器的可哈希性。
    """
    repr_options = options
    if isinstance(options, (list, dict, set)):
        options = tuple(options)

    return _InValidator(options, repr_options)


@attrs(repr=False, slots=False, unsafe_hash=True)
class _IsCallableValidator:
    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not callable(value):
            message = (
                "'{name}' must be callable "
                "(got {value!r} that is a {actual!r})."
            )
            raise NotCallableError(
                msg=message.format(
                    name=attr.name, value=value, actual=value.__class__
                ),
                value=value,
            )

    def __repr__(self):
        return "<is_callable validator>"


def is_callable():
    """
    一个验证器，如果初始化器被调用时为此特定属性提供的值不可调用，
    则会引发 `attrs.exceptions.NotCallableError`。

    .. versionadded:: 19.1.0

    Raises:
        attrs.exceptions.NotCallableError:
            带有可读性错误信息，包含属性
            (`attrs.Attribute`) 名称和获得的值。
    """
    return _IsCallableValidator()


@attrs(repr=False, slots=True, unsafe_hash=True)
class _DeepIterable:
    member_validator = attrib(validator=is_callable())
    iterable_validator = attrib(
        default=None, validator=optional(is_callable())
    )

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if self.iterable_validator is not None:
            self.iterable_validator(inst, attr, value)

        for member in value:
            self.member_validator(inst, attr, member)

    def __repr__(self):
        iterable_identifier = (
            ""
            if self.iterable_validator is None
            else f" {self.iterable_validator!r}"
        )
        return (
            f"<deep_iterable validator for{iterable_identifier}"
            f" iterables of {self.member_validator!r}>"
        )


def deep_iterable(member_validator, iterable_validator=None):
    """
    一个验证器，执行对可迭代对象的深度验证。

    Args:
        member_validator: 应用于可迭代成员的验证器。

        iterable_validator:
            应用于可迭代对象本身的验证器（可选）。

    Raises
        TypeError: 如果任何子验证器失败

    .. versionadded:: 19.1.0
    """
    if isinstance(member_validator, (list, tuple)):
        member_validator = and_(*member_validator)
    return _DeepIterable(member_validator, iterable_validator)


@attrs(repr=False, slots=True, unsafe_hash=True)
class _DeepMapping:
    key_validator = attrib(validator=is_callable())
    value_validator = attrib(validator=is_callable())
    mapping_validator = attrib(default=None, validator=optional(is_callable()))

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if self.mapping_validator is not None:
            self.mapping_validator(inst, attr, value)

        for key in value:
            self.key_validator(inst, attr, key)
            self.value_validator(inst, attr, value[key])

    def __repr__(self):
        return f"<deep_mapping validator for objects mapping {self.key_validator!r} to {self.value_validator!r}>"


def deep_mapping(key_validator, value_validator, mapping_validator=None):
    """
    一个验证器，执行对字典的深度验证。

    Args:
        key_validator: 应用于字典键的验证器。

        value_validator: 应用于字典值的验证器。

        mapping_validator:
            应用于顶层映射属性的验证器（可选）。

    .. versionadded:: 19.1.0

    Raises:
        TypeError: 如果任何子验证器失败
    """
    return _DeepMapping(key_validator, value_validator, mapping_validator)


@attrs(repr=False, frozen=True, slots=True)
class _NumberValidator:
    bound = attrib()
    compare_op = attrib()
    compare_func = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not self.compare_func(value, self.bound):
            msg = f"'{attr.name}' must be {self.compare_op} {self.bound}: {value}"
            raise ValueError(msg)

    def __repr__(self):
        return f"<Validator for x {self.compare_op} {self.bound}>"


def lt(val):
    """
    一个验证器，如果初始化器使用大于或等于 *val* 的数字调用，则引发 `ValueError` 。

    该验证器使用 `operator.lt` 来比较值。

    Args:
        val: 值的排他上界。

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<", operator.lt)


def le(val):
    """
    一个验证器，如果初始化器使用大于 *val* 的数字调用，则引发 `ValueError`。

    该验证器使用 `operator.le` 来比较值。

    Args:
        val: 值的包含上界。

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, "<=", operator.le)


def ge(val):
    """
    一个验证器，如果初始化器使用小于 *val* 的数字调用，则引发 `ValueError`。

    该验证器使用 `operator.ge` 来比较值。

    Args:
        val: 值的包含下界。

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">=", operator.ge)


def gt(val):
    """
    一个验证器，如果初始化器使用小于或等于 *val* 的数字调用，则引发 `ValueError`。

    该验证器使用 `operator.ge` 来比较值。

    Args:
       val: 值的排他下界。

    .. versionadded:: 21.3.0
    """
    return _NumberValidator(val, ">", operator.gt)


@attrs(repr=False, frozen=True, slots=True)
class _MaxLengthValidator:
    max_length = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if len(value) > self.max_length:
            msg = f"Length of '{attr.name}' must be <= {self.max_length}: {len(value)}"
            raise ValueError(msg)

    def __repr__(self):
        return f"<max_len validator for {self.max_length}>"


def max_len(length):
    """
    一个验证器，如果初始化器使用长度超过 *length* 的字符串或可迭代对象调用，则引发 `ValueError`。

    Args:
        length (int): 字符串或可迭代对象的最大长度

    .. versionadded:: 21.3.0
    """
    return _MaxLengthValidator(length)


@attrs(repr=False, frozen=True, slots=True)
class _MinLengthValidator:
    min_length = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if len(value) < self.min_length:
            msg = f"Length of '{attr.name}' must be >= {self.min_length}: {len(value)}"
            raise ValueError(msg)

    def __repr__(self):
        return f"<min_len validator for {self.min_length}>"


def min_len(length):
    """
    一个验证器，如果初始化器使用长度短于 *length* 的字符串或可迭代对象调用，则引发 `ValueError`。

    Args:
        length (int): 字符串或可迭代对象的最小长度

    .. versionadded:: 22.1.0
    """
    return _MinLengthValidator(length)


@attrs(repr=False, slots=True, unsafe_hash=True)
class _SubclassOfValidator:
    type = attrib()

    def __call__(self, inst, attr, value):
        """
        We use a callable class to be able to change the ``__repr__``.
        """
        if not issubclass(value, self.type):
            msg = f"'{attr.name}' must be a subclass of {self.type!r} (got {value!r})."
            raise TypeError(
                msg,
                attr,
                self.type,
                value,
            )

    def __repr__(self):
        return f"<subclass_of validator for type {self.type!r}>"


def _subclass_of(type):
    """
    A validator that raises a `TypeError` if the initializer is called with a
    wrong type for this particular attribute (checks are performed using
    `issubclass` therefore it's also valid to pass a tuple of types).

    Args:
        type (type | tuple[type, ...]): The type(s) to check for.

    Raises:
        TypeError:
            With a human readable error message, the attribute (of type
            `attrs.Attribute`), the expected type, and the value it got.
    """
    return _SubclassOfValidator(type)


@attrs(repr=False, slots=True, unsafe_hash=True)
class _NotValidator:
    validator = attrib()
    msg = attrib(
        converter=default_if_none(
            "not_ validator child '{validator!r}' "
            "did not raise a captured error"
        )
    )
    exc_types = attrib(
        validator=deep_iterable(
            member_validator=_subclass_of(Exception),
            iterable_validator=instance_of(tuple),
        ),
    )

    def __call__(self, inst, attr, value):
        try:
            self.validator(inst, attr, value)
        except self.exc_types:
            pass  # suppress error to invert validity
        else:
            raise ValueError(
                self.msg.format(
                    validator=self.validator,
                    exc_types=self.exc_types,
                ),
                attr,
                self.validator,
                value,
                self.exc_types,
            )

    def __repr__(self):
        return f"<not_ validator wrapping {self.validator!r}, capturing {self.exc_types!r}>"


def not_(validator, *, msg=None, exc_types=(ValueError, TypeError)):
    """
    一个包裹并逻辑上“反转”传入的验证器的验证器。
    如果提供的验证器*没有*引发 `ValueError` 或 `TypeError` （默认情况下），
    将抛出 `ValueError` ，并且如果提供的验证器*确实*引发异常，则会抑制该异常。

    旨在与现有验证器一起使用，以组合逻辑，而无需创建反转变体，例如，``not_(in_(...))``。

    Args:
        validator: 一个需要逻辑反转的验证器。

        msg (str):
            如果验证器失败时要抛出的消息。使用键 ``exc_types`` 和 ``validator`` 格式化。

        exc_types (tuple[type, ...]):
            要捕获的异常类型。子验证器引发的其他类型不会被拦截，将直接通过。

    Raises:
        ValueError:
            带有人类可读的错误消息，属性（类型为 `attrs.Attribute` ），未能引发异常的验证器，
            以及获取的值和预期的异常类型。

    .. versionadded:: 22.2.0
    """
    try:
        exc_types = tuple(exc_types)
    except TypeError:
        exc_types = (exc_types,)
    return _NotValidator(validator, msg, exc_types)


@attrs(repr=False, slots=True, unsafe_hash=True)
class _OrValidator:
    validators = attrib()

    def __call__(self, inst, attr, value):
        for v in self.validators:
            try:
                v(inst, attr, value)
            except Exception:  # noqa: BLE001, PERF203, S112
                continue
            else:
                return

        msg = f"None of {self.validators!r} satisfied for value {value!r}"
        raise ValueError(msg)

    def __repr__(self):
        return f"<or validator wrapping {self.validators!r}>"


def or_(*validators):
    """
    一个将多个验证器组合成一个的验证器。

    当在一个值上调用时，它会运行所有封装的验证器，直到满足其中一个。

    Args:
        validators (~collections.abc.Iterable[typing.Callable]):
            任意数量的验证器。

    Raises:
        ValueError:
            如果没有验证器被满足。会抛出一个可读性强的错误消息，列出所有封装的验证器和未通过的值。

    .. versionadded:: 24.1.0
    """
    vals = []
    for v in validators:
        vals.extend(v.validators if isinstance(v, _OrValidator) else [v])

    return _OrValidator(tuple(vals))
