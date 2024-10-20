# mypy: ignore-errors
# SPDX-License-Identifier: MIT

"""
These are keyword-only APIs that call `attr.s` and `attr.ib` with different
default values.
"""

from functools import partial

from . import setters
from ._funcs import asdict as _asdict
from ._funcs import astuple as _astuple
from ._make import (
    _DEFAULT_ON_SETATTR,
    NOTHING,
    _frozen_setattrs,
    attrib,
    attrs,
)
from .exceptions import UnannotatedAttributeError


def define(
    maybe_cls=None,
    *,
    these=None,
    repr=None,
    unsafe_hash=None,
    hash=None,
    init=None,
    slots=True,
    frozen=False,
    weakref_slot=True,
    str=False,
    auto_attribs=None,
    kw_only=False,
    cache_hash=False,
    auto_exc=True,
    eq=None,
    order=False,
    auto_detect=True,
    getstate_setstate=None,
    on_setattr=None,
    field_transformer=None,
    match_args=True,
):
    r"""
    一个类装饰器, 它根据使用 :doc:`类型注释 <types>` 、`field()` 调用或 *these* 参数指定的 :term:`fields(字段) <field>` , 添加 :term:`双下划线方法 <dunder methods>` 。

    由于 *attrs* 会对现有类进行修补或替换, 因此您无法在 *attrs* 类中使用 `object.__init_subclass__` , 因为它运行得太早。作为替代, 您可以在类上定义 ``__attrs_init_subclass__`` 。此方法将在 *attrs* 类创建后调用该子类。另请参见 :ref:`init-subclass` 。

    Args:
        slots (bool):
            创建一个更节省内存的 :term:`slotted class <slotted classes>` 。slotted 类通常优于默认的 dict 类, 但有一些您需要了解的注意事项, 因此我们建议您阅读 :term:`glossary entry <slotted classes>`。

        auto_detect (bool):
            不必显式设置 *init*、*repr*、*eq* 和 *hash* 参数, 假定它们被设置为 True **除非** 其中一个参数的相关方法在 *当前* 类中实现(意味着它并不是从某个基类继承的)。

            例如, 通过自己在类上实现 ``__eq__`` ,  *attrs* 将推断出 ``eq=False`` , 并且将不会创建 *neither* ``__eq__`` *nor* ``__ne__`` (但是 Python 类默认有一个合理的 ``__ne__``, 因此在大多数情况下仅实现 ``__eq__`` 应该足够)。

            将 True 或 False 传递给 *init*、*repr*、*eq* 或 *hash* 将覆盖 *auto_detect* 的任何判断。

        auto_exc (bool):
            如果类继承自 `BaseException` (隐含包括任何异常的子类), 则会表现得像一个行为良好的 Python 异常类：

            - *eq*、*order* 和 *hash* 的值将被忽略, 实例将根据实例的 ID 进行比较和哈希 [#]_, 
            - 所有传递给 ``__init__`` 或具有默认值的属性将额外作为元组在 ``args`` 属性中可用, 
            - *str* 的值将被忽略, ``__str__`` 将交给基类处理。

            .. [#]
                请注意, *attrs* 不会移除现有的 ``__hash__`` 或相等方法的实现。它只是不添加自己的实现。

        on_setattr (~typing.Callable | list[~typing.Callable] | None | ~typing.Literal[attrs.setters.NO_OP]):
            一个可调用对象, 在用户尝试设置属性(无论是通过赋值如 ``i.x = 42`` 还是使用 `setattr` 如 ``setattr(i, "x", 42)``)时运行。它接收与验证器相同的参数：实例、正在修改的属性和新值。

            如果没有引发异常, 该属性将被设置为可调用对象的返回值。

            如果传递了一个可调用对象的列表, 它们会自动包装在 `attrs.setters.pipe` 中。

            如果保持为 None, 默认行为是在设置属性时运行转换器和验证器。

        init (bool):
            创建一个 ``__init__`` 方法, 用于初始化 *attrs* 属性。参数名的前导下划线会被去掉, 除非在属性上设置了别名。

            .. seealso::
                `init` 显示了自定义生成的 ``__init__`` 方法的高级方法, 包括在前后执行代码。

        repr (bool):
            创建一个 ``__repr__`` 方法, 用于生成 *attrs* 属性的可读表示。

        str (bool):
            创建一个与 ``__repr__`` 相同的 ``__str__`` 方法。除非是 `Exception`, 通常不需要这样做。

        eq (bool | None):
            如果为 True 或 None(默认), 则添加 ``__eq__`` 和 ``__ne__`` 方法, 用于检查两个实例是否相等。

            .. seealso::
                `comparison` 描述了如何自定义比较行为, 甚至可以比较 NumPy 数组。

        order (bool | None):
            如果为 True, 添加 ``__lt__``、``__le__``、``__gt__`` 和 ``__ge__`` 方法, 这些方法的行为与上面的 *eq* 一样, 并允许实例进行排序。

            仅当两个类的类型完全相同时, 实例才会像它们的 *attrs* 属性元组一样进行比较。

            如果为 `None`, 则镜像 *eq* 的值。

            .. seealso:: `comparison`

        unsafe_hash (bool | None):
            如果为 None(默认), 则根据 *eq* 和 *frozen* 的设置生成 ``__hash__`` 方法。

            1. 如果 *两者* 为 True, *attrs* 将为您生成一个 ``__hash__``。
            2. 如果 *eq* 为 True 且 *frozen* 为 False, ``__hash__`` 将被设置为 None, 标记为不可哈希(确实如此)。
            3. 如果 *eq* 为 False, ``__hash__`` 将保持不变, 意味着将使用基类的 ``__hash__`` 方法。如果基类是 `object`, 这意味着将回退到基于 ID 的哈希。

            虽然不推荐, 您可以自行决定并强制 *attrs* 创建一个(例如, 如果类是不可变的, 即使您没有以编程方式冻结它)通过传递 True 或不传递。这两种情况都比较特殊, 应谨慎使用。

            .. seealso::
                - 我们关于 `hashing` 的文档, 
                - Python 关于 `object.__hash__` 的文档, 
                - 以及 `导致默认行为的 GitHub issue <https://github.com/python-attrs/attrs/issues/136>`_ 的更多细节。

        hash (bool | None):
            *unsafe_hash* 的弃用别名。*unsafe_hash* 优先。

        cache_hash (bool):
            确保对象的哈希码只计算一次并存储在对象上。如果设置为 True, 哈希必须显式或隐式启用。如果哈希码被缓存, 请避免在对象创建后对哈希码计算涉及的字段进行任何重新赋值或对这些字段指向的对象进行任何变更。如果发生这种变化, 对象的哈希码行为是未定义的。

        frozen (bool):
            使实例在初始化后不可变。如果有人试图修改一个冻结的实例, 将引发 `attrs.exceptions.FrozenInstanceError`。

            .. note::
                1. 这是通过在您的类上安装一个自定义的 ``__setattr__`` 方法实现的, 因此您无法实现自己的方法。

                2. 在 Python 中, 真正的不可变性是不可能的。

                3. 这 *确实* 对初始化新实例有轻微的运行时性能 `影响 <how-frozen>`。换句话说：使用 ``frozen=True`` 时, ``__init__`` 会稍微慢一些。

                4. 如果一个类被冻结, 您不能在 ``__attrs_post_init__`` 或自定义的 ``__init__`` 中修改 ``self``。您可以通过使用
                    ``object.__setattr__(self, "attribute_name", value)`` 来规避该限制。

                5. 冻结类的子类也会被冻结。

        kw_only (bool):
            使生成的 ``__init__`` 中所有属性仅限关键字参数(如果 *init* 为 False, 此参数将被忽略)。

        weakref_slot (bool):
            使实例可被弱引用。这在 *slots* 为 True 的情况下有效。

        field_transformer (~typing.Callable | None):
            一个函数, 在 *attrs* 最终确定类之前, 使用原始类对象和所有字段调用。您可以使用此功能, 例如, 自动根据字段的类型为字段添加转换器或验证器。

            .. seealso:: `transform-fields`

        match_args (bool):
            如果为 True(默认), 则在类上设置 ``__match_args__`` 以支持 :pep:`634` (*结构模式匹配*)。它是一个元组, 包含所有非关键字参数的 ``__init__`` 参数名, 仅在 Python 3.10 及更高版本中可用。在较旧的 Python 版本中被忽略。

        collect_by_mro (bool):
            如果为 True, *attrs* 将根据 `方法解析顺序
            <https://docs.python.org/3/howto/mro.html>`_ 正确收集基类的属性。如果为 False, *attrs* 将模仿(错误的) `dataclasses` 和 :pep:`681` 的行为。

            另请参见 `issue #428
            <https://github.com/python-attrs/attrs/issues/428>`_。

        getstate_setstate (bool | None):
            .. note::
                这通常仅对 slotted 类有趣, 您可能只需将 *auto_detect* 设置为 True。

            如果为 True, 将生成 ``__getstate__`` 和 ``__setstate__`` 并附加到类上。这对于 slotted 类能够被 pickle 是必要的。如果为 None, 则 slotted 类默认为 True, 而 dict 类为 False。

            如果 *auto_detect* 为 True, 且 *getstate_setstate* 为 None, 且 **任一** ``__getstate__`` 或 ``__setstate__`` 直接在类上被检测到(意味着：不是继承的), 则它将被设置为 False(这通常是您想要的)。

        auto_attribs (bool | None):
            如果为 True, 查看类型注解以确定使用哪些属性, 类似于 `dataclasses`。如果为 False, 则仅查找显式的 :func:`field` 类属性, 类似于经典的 *attrs*。

            如果为 None, 将进行推测：

            1. 如果有任何属性被注解且未找到未注解的 `attrs.field`, 则假设 *auto_attribs=True*。
            2. 否则, 假设 *auto_attribs=False* 并尝试收集 `attrs.field`。

            如果 *attrs* 决定查看类型注解, **所有** 字段 **必须** 被注解。如果 *attrs* 遇到一个设置为 :func:`field` / `attr.ib` 但缺少类型注解的字段, 将引发 `attrs.exceptions.UnannotatedAttributeError`。如果您不想设置类型, 请使用 ``field_name: typing.Any = field(...)``。

            .. warning::
                对于使用属性名称创建装饰器的功能(例如, :ref:`validators <validators>`), 您仍然 *必须* 将 :func:`field` / `attr.ib` 分配给它们。否则, Python 将无法找到名称或尝试使用默认值调用, 例如 ``validator``。

            被标注为 `typing.ClassVar` 的属性, 以及既没有被注解又没有设置为 `field()` 的属性将被 **忽略**。

        these (dict[str, object]):
            一个名称到 `field()` 返回值(私有)映射的字典。这对于避免在类体内定义您的属性很有用, 因为您不能(例如, 如果您想向 Django 模型添加 ``__repr__`` 方法)或不想这样做。

            如果 *these* 不为 `None`, *attrs* 将 *不* 在类体中搜索属性, 并且将 *不* 从中删除任何属性。

            顺序由 *these* 中属性的顺序推导得出。

            可以说, 这是一个相当晦涩的功能。

    .. versionadded:: 20.1.0  
    .. versionchanged:: 21.3.0 转换器也在 ``on_setattr`` 上运行。  
    .. versionadded:: 22.2.0  
        *unsafe_hash* 作为 *hash* 的别名(为了兼容 :pep:`681`)。  
    .. versionchanged:: 24.1.0  
        实例不再作为属性元组进行比较, 而是使用一个大的 ``and`` 条件。这更快, 并且对于无法比较的值(如 `math.nan`)具有更正确的行为。  
    .. versionadded:: 24.1.0  
        如果一个类有一个 *继承的* 类方法 ``__attrs_init_subclass__``, 它将在类创建后执行。  
    .. deprecated:: 24.1.0 *hash* 已被弃用, 取而代之的是 *unsafe_hash*。

    .. note::

        与经典的 `attr.s` 的主要区别如下：

        - 自动检测 *auto_attribs* 是否应为 `True`
            (参见 *auto_attribs* 参数)。
        - 当属性被设置时, 转换器和验证器默认运行 --
            如果 *frozen* 为 `False`。
        - *slots=True*

            通常, 这只有好处, 并且在日常编程中几乎没有可见效果。但它 *可能* 导致一些意外行为, 因此请确保阅读 :term:`slotted classes`。

        - *auto_exc=True*  
        - *auto_detect=True*  
        - *order=False*  
        - 一些仅在 Python 2 中相关或为向后兼容而保留的选项已被删除。

    """

    def do_it(cls, auto_attribs):
        return attrs(
            maybe_cls=cls,
            these=these,
            repr=repr,
            hash=hash,
            unsafe_hash=unsafe_hash,
            init=init,
            slots=slots,
            frozen=frozen,
            weakref_slot=weakref_slot,
            str=str,
            auto_attribs=auto_attribs,
            kw_only=kw_only,
            cache_hash=cache_hash,
            auto_exc=auto_exc,
            eq=eq,
            order=order,
            auto_detect=auto_detect,
            collect_by_mro=True,
            getstate_setstate=getstate_setstate,
            on_setattr=on_setattr,
            field_transformer=field_transformer,
            match_args=match_args,
        )

    def wrap(cls):
        """
        将其作为包装器可以确保此代码在类创建期间运行。

        我们还确保类的冻结状态(frozen-ness)是可继承的。
        """
        nonlocal frozen, on_setattr

        had_on_setattr = on_setattr not in (None, setters.NO_OP)

        # By default, mutable classes convert & validate on setattr.
        if frozen is False and on_setattr is None:
            on_setattr = _DEFAULT_ON_SETATTR

        # However, if we subclass a frozen class, we inherit the immutability
        # and disable on_setattr.
        for base_cls in cls.__bases__:
            if base_cls.__setattr__ is _frozen_setattrs:
                if had_on_setattr:
                    msg = "Frozen classes can't use on_setattr (frozen-ness was inherited)."
                    raise ValueError(msg)

                on_setattr = setters.NO_OP
                break

        if auto_attribs is not None:
            return do_it(cls, auto_attribs)

        try:
            return do_it(cls, True)
        except UnannotatedAttributeError:
            return do_it(cls, False)

    # maybe_cls's type depends on the usage of the decorator.  It's a class
    # if it's used as `@attrs` but `None` if used as `@attrs()`.
    if maybe_cls is None:
        return wrap

    return wrap(maybe_cls)


mutable = define
frozen = partial(define, frozen=True, on_setattr=None)


def field(
    *,
    default=NOTHING,
    validator=None,
    repr=True,
    hash=None,
    init=True,
    metadata=None,
    type=None,
    converter=None,
    factory=None,
    kw_only=False,
    eq=None,
    order=None,
    on_setattr=None,
    alias=None,
):
    """
    创建一个新的 :term:`field` / :term:`attribute` 在类上。

    .. warning::

        除非该类也使用 `attrs.define` (或类似的)进行装饰, 否则 **无任何作用** !

    Args:
        default:
            如果使用 *attrs* 生成的 ``__init__`` 方法且在实例化时未传递值, 或者使用 ``init=False`` 排除了该属性, 则使用此值。

            如果该值是 `attrs.Factory` 的实例, 则会使用其可调用对象构造新值(对于可变数据类型, 如列表或字典, 非常有用)。

            如果未设置默认值(或手动设置为 `attrs.NOTHING` ), 则在实例化时必须提供一个值;否则会引发 `TypeError` 。

            .. seealso:: `defaults`

        factory (~typing.Callable):
            ``default=attr.Factory(factory)`` 的语法糖。

        validator (~typing.Callable | list[~typing.Callable]):
            可调用对象, 在 *attrs* 生成的 ``__init__`` 方法调用后被调用。它们接收已初始化的实例、:func:`~attrs.Attribute` 和传入的值。

            返回值不会被检查, 因此验证器必须自己抛出异常。

            如果传入一个 `list` , 其项将被视为验证器, 且必须全部通过。

            可以使用 `attrs.validators.get_disabled` / `attrs.validators.set_disabled` 全局禁用和重新启用验证器。

            验证器也可以使用装饰器语法设置, 如下所示。

            .. seealso:: :ref:`validators`

        repr (bool | ~typing.Callable):
            在生成的 ``__repr__`` 方法中包含此属性。如果为 True, 则包含该属性;如果为 False, 则省略它。默认情况下, 使用内置的 ``repr()`` 函数。要覆盖属性值的格式, 可以传递一个可调用对象, 该对象接受一个值并返回一个字符串。请注意, 结果字符串将原样使用, 这意味着它将直接用于替代调用 ``repr()``(默认)。

        eq (bool | ~typing.Callable):
            如果为 True(默认), 则在生成的 ``__eq__`` 和 ``__ne__`` 方法中包含此属性, 以检查两个实例的相等性。要覆盖属性值的比较方式, 可以传递一个可调用对象, 该对象接受一个值并返回要比较的值。

            .. seealso:: `comparison`

        order (bool | ~typing.Callable):
            如果为 True(默认), 则在生成的 ``__lt__``、``__le__``、``__gt__`` 和 ``__ge__`` 方法中包含此属性。要覆盖属性值的排序方式, 可以传递一个可调用对象, 该对象接受一个值并返回要排序的值。

            .. seealso:: `comparison`

        hash (bool | None):
            在生成的 ``__hash__`` 方法中包含此属性。如果为 None(默认), 则反映 *eq* 的值。这是根据 Python 规范的正确行为。将此值设置为其他任何值都*不推荐*。

            .. seealso:: `hashing`

        init (bool):
            在生成的 ``__init__`` 方法中包含此属性。

            可以将其设置为 False, 并设置默认值。在这种情况下, 此属性将无条件地使用指定的默认值或工厂进行初始化。

            .. seealso:: `init`

        converter (typing.Callable | Converter):
            一个可调用对象, 由 *attrs* 生成的 ``__init__`` 方法调用, 以将属性值转换为所需的格式。

            如果传递的是普通的可调用对象, 它将作为唯一的位置参数传递传入的值。通过将可调用对象包装在 `Converter` 中, 可以接收额外的参数。

            无论哪种方式, 返回的值将用作属性的新值。在传递给验证器之前(如果有的话)将进行值的转换。

            .. seealso:: :ref:`converters`

        metadata (dict | None):
            一个任意映射, 用于第三方代码。

            .. seealso:: `extending-metadata`。

        type (type):
            属性的类型。现在, 指定类型的首选方法是使用变量注释(见 :pep:`526`)。此参数是为了向后兼容和与 `make_class` 一起使用。无论使用何种方法, 类型将存储在 ``Attribute.type`` 中。

            请注意, *attrs* 本身并不会对该元数据执行任何操作。您可以将其作为自己代码的一部分或用于 `静态类型检查 <types>`。

        kw_only (bool):
            在生成的 ``__init__`` 中将此属性设置为仅通过关键字传递(如果 ``init`` 为 False, 则此参数被忽略)。

        on_setattr (~typing.Callable | list[~typing.Callable] | None | ~typing.Literal[attrs.setters.NO_OP]):
            允许覆盖来自 `attr.s` 的 *on_setattr* 设置。如果留空为 None, 将使用来自 `attr.s` 的 *on_setattr* 值。设置为 `attrs.setters.NO_OP` 可对该属性**不**运行任何 `setattr` 钩子——无论 `define()` 中的设置如何。

        alias (str | None):
            在生成的 ``__init__`` 方法中覆盖此属性的参数名称。如果留空为 None, 则默认为 ``name``, 去掉前导下划线。请参见 `private-attributes`。

    .. versionadded:: 20.1.0
    .. versionchanged:: 21.1.0
       *eq*, *order*, 和 *cmp* 同样接受自定义的 callable
    .. versionadded:: 22.2.0 *alias*
    .. versionadded:: 23.1.0
       *type* 参数已重新添加;主要是为了 `attrs.make_class` 。请注意, 类型检查器会忽略这些元数据。

    .. seealso::

       `attr.ib`
    """
    return attrib(
        default=default,
        validator=validator,
        repr=repr,
        hash=hash,
        init=init,
        metadata=metadata,
        type=type,
        converter=converter,
        factory=factory,
        kw_only=kw_only,
        eq=eq,
        order=order,
        on_setattr=on_setattr,
        alias=alias,
    )


def asdict(inst, *, recurse=True, filter=None, value_serializer=None):
    """
    Same as `attr.asdict`, except that collections types are always retained
    and dict is always used as *dict_factory*.

    与 `attr.asdict` 相同, 但集合类型始终被保留, 并且字典(dict)始终使用 *dict_factory*。

    .. versionadded:: 21.3.0
    """
    return _asdict(
        inst=inst,
        recurse=recurse,
        filter=filter,
        value_serializer=value_serializer,
        retain_collection_types=True,
    )


def astuple(inst, *, recurse=True, filter=None):
    """
    与 `attr.asdict` 相同, 但集合类型始终被保留, 并且元素(`tuple`)始终使用 *tuple_factory*。

    .. versionadded:: 21.3.0
    """
    return _astuple(
        inst=inst, recurse=recurse, filter=filter, retain_collection_types=True
    )
