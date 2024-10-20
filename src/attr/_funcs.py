# mypy: ignore-errors
# SPDX-License-Identifier: MIT


import copy

from ._compat import PY_3_9_PLUS, get_generic_base
from ._make import _OBJ_SETATTR, NOTHING, fields
from .exceptions import AttrsAttributeNotFoundError


def asdict(
    inst,
    recurse=True,
    filter=None,
    dict_factory=dict,
    retain_collection_types=False,
    value_serializer=None,
):
    """
    返回 *inst* 的 *attrs* 属性值作为字典。

    可选择递归进入其他 *attrs* 装饰的类。

    Args:
        inst: 一个 *attrs* 装饰类的实例。

        recurse (bool): 递归进入也被 *attrs* 装饰的类。

        filter (~typing.Callable):
            一个可调用对象，其返回值决定一个属性或元素是否包含（`True`）或被丢弃（`False`）。作为第一个参数调用 `attrs.Attribute`，第二个参数为值。

        dict_factory (~typing.Callable):
            用于生成字典的可调用对象。例如，为了生成有序字典而不是普通的 Python 字典，可以传入 ``collections.OrderedDict``。

        retain_collection_types (bool):
            遇到类型为 `tuple` 或 `set` 的属性时，不转换为 `list`。仅在 *recurse* 为 `True` 时有意义。

        value_serializer (typing.Callable | None):
            针对每个属性或字典键/值调用的钩子。它接收当前实例、字段和值，并必须返回（更新后的）值。该钩子在应用可选的 *filter* 后运行。

    Returns:
        返回类型为 *dict_factory*。

    Raises:
        attrs.exceptions.NotAnAttrsClassError:
            如果 *cls* 不是一个 *attrs* 类。

    ..  versionadded:: 16.0.0 *dict_factory*
    ..  versionadded:: 16.1.0 *retain_collection_types*
    ..  versionadded:: 20.3.0 *value_serializer*
    ..  versionadded:: 21.3.0
        如果字典中有一个键的集合，则将其序列化为元组。
    """
    attrs = fields(inst.__class__)
    rv = dict_factory()
    for a in attrs:
        v = getattr(inst, a.name)
        if filter is not None and not filter(a, v):
            continue

        if value_serializer is not None:
            v = value_serializer(inst, a, v)

        if recurse is True:
            if has(v.__class__):
                rv[a.name] = asdict(
                    v,
                    recurse=True,
                    filter=filter,
                    dict_factory=dict_factory,
                    retain_collection_types=retain_collection_types,
                    value_serializer=value_serializer,
                )
            elif isinstance(v, (tuple, list, set, frozenset)):
                cf = v.__class__ if retain_collection_types is True else list
                items = [
                    _asdict_anything(
                        i,
                        is_key=False,
                        filter=filter,
                        dict_factory=dict_factory,
                        retain_collection_types=retain_collection_types,
                        value_serializer=value_serializer,
                    )
                    for i in v
                ]
                try:
                    rv[a.name] = cf(items)
                except TypeError:
                    if not issubclass(cf, tuple):
                        raise
                    # Workaround for TypeError: cf.__new__() missing 1 required
                    # positional argument (which appears, for a namedturle)
                    rv[a.name] = cf(*items)
            elif isinstance(v, dict):
                df = dict_factory
                rv[a.name] = df(
                    (
                        _asdict_anything(
                            kk,
                            is_key=True,
                            filter=filter,
                            dict_factory=df,
                            retain_collection_types=retain_collection_types,
                            value_serializer=value_serializer,
                        ),
                        _asdict_anything(
                            vv,
                            is_key=False,
                            filter=filter,
                            dict_factory=df,
                            retain_collection_types=retain_collection_types,
                            value_serializer=value_serializer,
                        ),
                    )
                    for kk, vv in v.items()
                )
            else:
                rv[a.name] = v
        else:
            rv[a.name] = v
    return rv


def _asdict_anything(
    val,
    is_key,
    filter,
    dict_factory,
    retain_collection_types,
    value_serializer,
):
    """
    ``asdict`` only works on attrs instances, this works on anything.
    """
    if getattr(val.__class__, "__attrs_attrs__", None) is not None:
        # Attrs class.
        rv = asdict(
            val,
            recurse=True,
            filter=filter,
            dict_factory=dict_factory,
            retain_collection_types=retain_collection_types,
            value_serializer=value_serializer,
        )
    elif isinstance(val, (tuple, list, set, frozenset)):
        if retain_collection_types is True:
            cf = val.__class__
        elif is_key:
            cf = tuple
        else:
            cf = list

        rv = cf(
            [
                _asdict_anything(
                    i,
                    is_key=False,
                    filter=filter,
                    dict_factory=dict_factory,
                    retain_collection_types=retain_collection_types,
                    value_serializer=value_serializer,
                )
                for i in val
            ]
        )
    elif isinstance(val, dict):
        df = dict_factory
        rv = df(
            (
                _asdict_anything(
                    kk,
                    is_key=True,
                    filter=filter,
                    dict_factory=df,
                    retain_collection_types=retain_collection_types,
                    value_serializer=value_serializer,
                ),
                _asdict_anything(
                    vv,
                    is_key=False,
                    filter=filter,
                    dict_factory=df,
                    retain_collection_types=retain_collection_types,
                    value_serializer=value_serializer,
                ),
            )
            for kk, vv in val.items()
        )
    else:
        rv = val
        if value_serializer is not None:
            rv = value_serializer(None, None, rv)

    return rv


def astuple(
    inst,
    recurse=True,
    filter=None,
    tuple_factory=tuple,
    retain_collection_types=False,
):
    """
    返回 *inst* 的 *attrs* 属性值作为元组。

    可选择递归进入其他 *attrs* 装饰的类。

    Args:
        inst: *attrs* 装饰类的实例。

        recurse (bool):
            是否递归进入同样被 *attrs* 装饰的类。

        filter (~typing.Callable):
            一个可调用对象，其返回值决定了属性或元素是被包含（`True`）还是被丢弃（`False`）。该函数的第一个参数为 `attrs.Attribute`，第二个参数为值。

        tuple_factory (~typing.Callable):
            用于生成元组的可调用对象。例如，可以生成列表而不是元组。

        retain_collection_types (bool):
            遇到类型为 `tuple`、`dict` 或 `set` 的属性时，不进行转换为 `list` 或 `dict`。只有在 *recurse* 为 `True` 时才有意义。

    Returns:
        返回 *tuple_factory* 的类型。

    Raises:
        attrs.exceptions.NotAnAttrsClassError:
            如果 *cls* 不是一个 *attrs* 类。

    .. versionadded:: 16.2.0
    """
    attrs = fields(inst.__class__)
    rv = []
    retain = retain_collection_types  # Very long. :/
    for a in attrs:
        v = getattr(inst, a.name)
        if filter is not None and not filter(a, v):
            continue
        if recurse is True:
            if has(v.__class__):
                rv.append(
                    astuple(
                        v,
                        recurse=True,
                        filter=filter,
                        tuple_factory=tuple_factory,
                        retain_collection_types=retain,
                    )
                )
            elif isinstance(v, (tuple, list, set, frozenset)):
                cf = v.__class__ if retain is True else list
                items = [
                    (
                        astuple(
                            j,
                            recurse=True,
                            filter=filter,
                            tuple_factory=tuple_factory,
                            retain_collection_types=retain,
                        )
                        if has(j.__class__)
                        else j
                    )
                    for j in v
                ]
                try:
                    rv.append(cf(items))
                except TypeError:
                    if not issubclass(cf, tuple):
                        raise
                    # Workaround for TypeError: cf.__new__() missing 1 required
                    # positional argument (which appears, for a namedturle)
                    rv.append(cf(*items))
            elif isinstance(v, dict):
                df = v.__class__ if retain is True else dict
                rv.append(
                    df(
                        (
                            (
                                astuple(
                                    kk,
                                    tuple_factory=tuple_factory,
                                    retain_collection_types=retain,
                                )
                                if has(kk.__class__)
                                else kk
                            ),
                            (
                                astuple(
                                    vv,
                                    tuple_factory=tuple_factory,
                                    retain_collection_types=retain,
                                )
                                if has(vv.__class__)
                                else vv
                            ),
                        )
                        for kk, vv in v.items()
                    )
                )
            else:
                rv.append(v)
        else:
            rv.append(v)

    return rv if tuple_factory is list else tuple_factory(rv)


def has(cls):
    """
    检查 *cls* 是否是具有 *attrs* 属性的类。

    Args:
        cls (type): 要检查的Class.

    Raises:
        TypeError: 如果 *cls* 不是一个类(class).

    Returns:
        bool:
    """
    attrs = getattr(cls, "__attrs_attrs__", None)
    if attrs is not None:
        return True

    # No attrs, maybe it's a specialized generic (A[str])?
    generic_base = get_generic_base(cls)
    if generic_base is not None:
        generic_attrs = getattr(generic_base, "__attrs_attrs__", None)
        if generic_attrs is not None:
            # Stick it on here for speed next time.
            cls.__attrs_attrs__ = generic_attrs
        return generic_attrs is not None
    return False


def assoc(inst, **changes):
    """
    复制 *inst* 并应用 *changes*。

    这与 `evolve` 不同，后者将更改应用于创建新实例的参数。

    `evolve` 的行为是更可取的，但存在一些 `边缘情况`_ ，在这些情况下它不起作用。因此 `assoc` 被弃用，但不会被移除。

    .. _`边缘情况`: https://github.com/python-attrs/attrs/issues/251

    Args:
        inst: 带有 *attrs* 属性的类的实例。

        changes: 新副本中的关键字更改。

    Returns:
        一个包含 *changes* 的 *inst* 的副本。

    Raises:
        attrs.exceptions.AttrsAttributeNotFoundError:
            如果在 *cls* 上找不到 *attr_name*。

        attrs.exceptions.NotAnAttrsClassError:
            如果 *cls* 不是一个 *attrs* 类。

    ..  deprecated:: 17.1.0
        如果可以，请改用 `attrs.evolve`。由于与 `attrs.evolve` 的略微不同的方法，这个函数不会被移除。
    """
    new = copy.copy(inst)
    attrs = fields(inst.__class__)
    for k, v in changes.items():
        a = getattr(attrs, k, NOTHING)
        if a is NOTHING:
            msg = f"{k} is not an attrs attribute on {new.__class__}."
            raise AttrsAttributeNotFoundError(msg)
        _OBJ_SETATTR(new, k, v)
    return new


def evolve(*args, **changes):
    """
    创建一个新实例，基于第一个位置参数并应用 *更改(changes)*。

    Args:

        inst:
            包含 *attrs* 属性的类的实例。*inst* 必须作为位置参数传递。

        changes:
            新副本中的关键字更改。

    Returns:
        一个包含 *changes* 的 inst 的副本。

    Raises:
        TypeError:
            如果在类的 ``__init__`` 中找不到 *attr_name*。

        attrs.exceptions.NotAnAttrsClassError:
            如果 *cls* 不是一个 *attrs* 类。

    .. versionadded:: 17.1.0
    .. deprecated:: 23.1.0
        现在不建议使用关键字参数 *inst* 来传递实例。直到 2024 年 4 月之前将引发警告，之后将变为错误。始终将实例作为位置参数传递。
    .. versionchanged:: 24.1.0
        *inst* 不能再作为关键字参数传递。
    """
    try:
        (inst,) = args
    except ValueError:
        msg = (
            f"evolve() takes 1 positional argument, but {len(args)} were given"
        )
        raise TypeError(msg) from None

    cls = inst.__class__
    attrs = fields(cls)
    for a in attrs:
        if not a.init:
            continue
        attr_name = a.name  # To deal with private attributes.
        init_name = a.alias
        if init_name not in changes:
            changes[init_name] = getattr(inst, attr_name)

    return cls(**changes)


def resolve_types(
    cls, globalns=None, localns=None, attribs=None, include_extras=True
):
    """
    解析类型注解中的任何字符串和前向注解(forward annotations)。

    这仅在你需要在 :class:`Attribute` 的 *type* 字段中使用具体类型时才需要。换句话说，如果你只是用于静态类型检查，则无需解析你的类型。

    如果没有参数，名称将会在创建类的模块中查找。如果这不是你想要的，例如，如果名称仅存在于方法内部，你可以传递 *globalns* 或 *localns* 来指定其他字典以查找这些名称。有关更多详细信息，请参见 `typing.get_type_hints` 的文档。

    Args:
        cls (type): 要解析的类。

        globalns (dict | None): 包含全局变量的字典。

        localns (dict | None): 包含局部变量的字典。

        attribs (list | None):
            给定类的 attribs 列表。当从 ``field_transformer`` 内部调用时，这是必要的，因为 *cls* 还不是一个 *attrs* 类。

        include_extras (bool):
            如果可能，更准确地解析。如果类型模块支持，传递 ``include_extras`` 到 ``typing.get_hints`` 。在支持的 Python 版本（3.9+）上，这将更准确地解析类型。

    Raises:
        TypeError: 如果 *cls* 不是一个类。

        attrs.exceptions.NotAnAttrsClassError:
            如果 *cls* 不是一个 *attrs* 类，并且你没有传递任何 attribs 。

        NameError: 如果因为缺少变量而无法解析类型。

    Returns:
        *cls*，这样你也可以将此函数用作类装饰器。请注意，必须在 `attrs.define` **之后** 应用它。这意味着装饰器必须在 `attrs.define` **之前** 出现。

    ..  versionadded:: 20.1.0
    ..  versionadded:: 21.1.0 *attribs*
    ..  versionadded:: 23.1.0 *include_extras*
    """
    # Since calling get_type_hints is expensive we cache whether we've
    # done it already.
    if getattr(cls, "__attrs_types_resolved__", None) != cls:
        import typing

        kwargs = {"globalns": globalns, "localns": localns}

        if PY_3_9_PLUS:
            kwargs["include_extras"] = include_extras

        hints = typing.get_type_hints(cls, **kwargs)
        for field in fields(cls) if attribs is None else attribs:
            if field.name in hints:
                # Since fields have been frozen we must work around it.
                _OBJ_SETATTR(field, "type", hints[field.name])
        # We store the class we resolved so that subclasses know they haven't
        # been resolved.
        cls.__attrs_types_resolved__ = cls

    # Return the class so you can use it as a decorator too.
    return cls
