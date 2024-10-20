API 参考
=============

.. module:: attrs

*attrs* 通过使用 `attrs.define` 或 `attr.s` 装饰类，然后使用 `attrs.field`、`attr.ib` 或类型注释在类上定义属性来工作。

以下是供理解 *attrs* 工作原理的人员阅读的干燥 API 说明。  
如果您想要一个实践教程，请查看 `examples`。

如果您对许多名称感到困惑，请查看 `names` 以获得澄清，但 `TL;DR <https://en.wikipedia.org/wiki/TL;DR>`_ 是，从版本 21.3.0 开始，*attrs* 由 **两个** 顶级包名称组成：

- 经典的 ``attr``，为尊贵的 `attr.s` 和 `attr.ib` 提供支持。
- 更新的 ``attrs``，仅包含大多数现代 API，并依赖 `attrs.define` 和 `attrs.field` 来定义您的类。  
  此外，一些在 ``attr`` 中也存在的 API 具有更好的默认值（例如，`attrs.asdict`）。

``attrs`` 命名空间是 *在* ``attr`` 之上构建的——``attr`` 将 *永远* 存在——并且同样稳定，因为它并不构成重写。  
为了降低重复性并使文档保持在合理的大小， ``attr`` 命名空间在 `在单独的页面上记录 <api-attr>` 上有单独的文档。


核心(Core)
------------

.. autofunction:: attrs.define

.. function:: mutable(same_as_define)

   与 `attrs.define` 相同。

   .. versionadded:: 20.1.0

.. function:: frozen(same_as_define)

   行为与 `attrs.define` 相同，但设置 *frozen=True* 和 *on_setattr=None* 。

   .. versionadded:: 20.1.0

.. autofunction:: field

.. autoclass:: Attribute
   :members: evolve

   例如：

   .. doctest::

      >>> import attrs
      >>> from attrs import define, field

      >>> @define
      ... class C:
      ...     x = field()
      >>> attrs.fields(C).x
      Attribute(name='x', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='x')


.. autofunction:: make_class

   如果你想以编程方式创建类，这非常方便。

   例如:

   .. doctest::

      >>> C1 = attrs.make_class("C1", ["x", "y"])
      >>> C1(1, 2)
      C1(x=1, y=2)
      >>> C2 = attrs.make_class("C2", {
      ...     "x": field(default=42),
      ...     "y": field(factory=list)
      ... })
      >>> C2()
      C2(x=42, y=[])


.. autoclass:: Factory

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(default=attrs.Factory(list))
      ...     y = field(default=attrs.Factory(
      ...         lambda self: set(self.x),
      ...         takes_self=True)
      ...     )
      >>> C()
      C(x=[], y=set())
      >>> C([1, 2, 3])
      C(x=[1, 2, 3], y={1, 2, 3})


.. autodata:: attrs.NOTHING
   :no-value:


Exceptions
----------

.. module:: attrs.exceptions

所有异常都可以通过 ``attr.exceptions`` 和 ``attrs.exceptions`` 获得，它们是相同的。这意味着它们被引发和/或捕获的命名空间无关紧要：

.. doctest::

   >>> import attrs, attr
   >>> try:
   ...     raise attrs.exceptions.FrozenError()
   ... except attr.exceptions.FrozenError:
   ...     print("this works!")
   this works!

.. autoexception:: PythonTooOldError
.. autoexception:: FrozenError
.. autoexception:: FrozenInstanceError
.. autoexception:: FrozenAttributeError
.. autoexception:: AttrsAttributeNotFoundError
.. autoexception:: NotAnAttrsClassError
.. autoexception:: DefaultAlreadySetError
.. autoexception:: NotCallableError
.. autoexception:: UnannotatedAttributeError

   例如::

       @attr.s(auto_attribs=True)
       class C:
           x: int
           y = attr.ib()  # <- ERROR!


.. _helpers:

Helpers
-------

*attrs* 提供了一些辅助方法，使得使用它更加容易：

.. currentmodule:: attrs

.. autofunction:: attrs.cmp_using

.. autofunction:: attrs.fields

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field()
      ...     y = field()
      >>> attrs.fields(C)
      (Attribute(name='x', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='x'), Attribute(name='y', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='y'))
      >>> attrs.fields(C)[1]
      Attribute(name='y', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='y')
      >>> attrs.fields(C).y is attrs.fields(C)[1]
      True

.. autofunction:: attrs.fields_dict

   例如:

   .. doctest::

      >>> @attr.s
      ... class C:
      ...     x = attr.ib()
      ...     y = attr.ib()
      >>> attrs.fields_dict(C)
      {'x': Attribute(name='x', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='x'), 'y': Attribute(name='y', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='y')}
      >>> attr.fields_dict(C)['y']
      Attribute(name='y', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='y')
      >>> attrs.fields_dict(C)['y'] is attrs.fields(C).y
      True

.. autofunction:: attrs.has

   例如:

   .. doctest::

      >>> @attr.s
      ... class C:
      ...     pass
      >>> attr.has(C)
      True
      >>> attr.has(object)
      False

.. autofunction:: attrs.resolve_types

    例如:

    .. doctest::

        >>> import typing
        >>> @define
        ... class A:
        ...     a: typing.List['A']
        ...     b: 'B'
        ...
        >>> @define
        ... class B:
        ...     a: A
        ...
        >>> attrs.fields(A).a.type
        typing.List[ForwardRef('A')]
        >>> attrs.fields(A).b.type
        'B'
        >>> attrs.resolve_types(A, globals(), locals())
        <class 'A'>
        >>> attrs.fields(A).a.type
        typing.List[A]
        >>> attrs.fields(A).b.type
        <class 'B'>

.. autofunction:: attrs.asdict

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x: int
      ...     y: int
      >>> attrs.asdict(C(1, C(2, 3)))
      {'x': 1, 'y': {'x': 2, 'y': 3}}

.. autofunction:: attrs.astuple

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field()
      ...     y = field()
      >>> attrs.astuple(C(1,2))
      (1, 2)

.. module:: attrs.filters

*attrs* 提供了用于过滤 `attrs.asdict` 和 `attrs.astuple` 中属性的辅助工具：

.. autofunction:: include

.. autofunction:: exclude

见 :func:`attrs.asdict` 的示例.

来自 ``attrs.filters`` 的所有对象也可以从 ``attr.filters`` 访问（这是同一个模块在不同命名空间中的表现）。

----

.. currentmodule:: attrs

.. autofunction:: attrs.evolve

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x: int
      ...     y: int
      >>> i1 = C(1, 2)
      >>> i1
      C(x=1, y=2)
      >>> i2 = attrs.evolve(i1, y=3)
      >>> i2
      C(x=1, y=3)
      >>> i1 == i2
      False

   ``evolve`` 使用 ``__init__`` 创建一个新实例。
   这一事实有几个影响：

   * 私有属性应当不带前导下划线进行指定，和 ``__init__`` 中一样。
   * 带有 ``init=False`` 的属性不能通过 ``evolve`` 进行设置。
   * 通常的 ``__init__`` 验证器将验证新值。

.. autofunction:: attrs.validate

   例如:

   .. doctest::

      >>> @define(on_setattr=attrs.setters.NO_OP)
      ... class C:
      ...     x = field(validator=attrs.validators.instance_of(int))
      >>> i = C(1)
      >>> i.x = "1"
      >>> attrs.validate(i)
      Traceback (most recent call last):
         ...
      TypeError: ("'x' must be <class 'int'> (got '1' that is a <class 'str'>).", ...)


.. _api-validators:

Validators
----------

.. module:: attrs.validators

``*attrs*`` 附带了一些常用的验证器，位于 ``attrs.validators`` 模块中。
所有来自 ``attrs.validators`` 的对象也可以通过 ``attr.validators`` 获得（这两个模块在不同的命名空间中是相同的）。

.. autofunction:: attrs.validators.lt

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(validator=attrs.validators.lt(42))
      >>> C(41)
      C(x=41)
      >>> C(42)
      Traceback (most recent call last):
         ...
      ValueError: ("'x' must be < 42: 42")

.. autofunction:: attrs.validators.le

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(validator=attrs.validators.le(42))
      >>> C(42)
      C(x=42)
      >>> C(43)
      Traceback (most recent call last):
         ...
      ValueError: ("'x' must be <= 42: 43")

.. autofunction:: attrs.validators.ge

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = attrs.field(validator=attrs.validators.ge(42))
      >>> C(42)
      C(x=42)
      >>> C(41)
      Traceback (most recent call last):
         ...
      ValueError: ("'x' must be => 42: 41")

.. autofunction:: attrs.validators.gt

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(validator=attrs.validators.gt(42))
      >>> C(43)
      C(x=43)
      >>> C(42)
      Traceback (most recent call last):
         ...
      ValueError: ("'x' must be > 42: 42")

.. autofunction:: attrs.validators.max_len

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(validator=attrs.validators.max_len(4))
      >>> C("spam")
      C(x='spam')
      >>> C("bacon")
      Traceback (most recent call last):
         ...
      ValueError: ("Length of 'x' must be <= 4: 5")

.. autofunction:: attrs.validators.min_len

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(validator=attrs.validators.min_len(1))
      >>> C("bacon")
      C(x='bacon')
      >>> C("")
      Traceback (most recent call last):
         ...
      ValueError: ("Length of 'x' must be => 1: 0")

.. autofunction:: attrs.validators.instance_of

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(validator=attrs.validators.instance_of(int))
      >>> C(42)
      C(x=42)
      >>> C("42")
      Traceback (most recent call last):
         ...
      TypeError: ("'x' must be <type 'int'> (got '42' that is a <type 'str'>).", Attribute(name='x', default=NOTHING, validator=<instance_of validator for type <type 'int'>>, type=None, kw_only=False), <type 'int'>, '42')
      >>> C(None)
      Traceback (most recent call last):
         ...
      TypeError: ("'x' must be <type 'int'> (got None that is a <type 'NoneType'>).", Attribute(name='x', default=NOTHING, validator=<instance_of validator for type <type 'int'>>, repr=True, cmp=True, hash=None, init=True, type=None, kw_only=False), <type 'int'>, None)

.. autofunction:: attrs.validators.in_

   例如:

   .. doctest::

      >>> import enum
      >>> class State(enum.Enum):
      ...     ON = "on"
      ...     OFF = "off"
      >>> @define
      ... class C:
      ...     state = field(validator=attrs.validators.in_(State))
      ...     val = field(validator=attrs.validators.in_([1, 2, 3]))
      >>> C(State.ON, 1)
      C(state=<State.ON: 'on'>, val=1)
      >>> C("On", 1)
      Traceback (most recent call last):
         ...
      ValueError: 'state' must be in <enum 'State'> (got 'On'), Attribute(name='state', default=NOTHING, validator=<in_ validator with options <enum 'State'>>, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False, inherited=False, on_setattr=None), <enum 'State'>, 'on')
      >>> C(State.ON, 4)
      Traceback (most recent call last):
      ...
      ValueError: 'val' must be in [1, 2, 3] (got 4), Attribute(name='val', default=NOTHING, validator=<in_ validator with options [1, 2, 3]>, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False, inherited=False, on_setattr=None), [1, 2, 3], 4)

.. autofunction:: attrs.validators.and_

   为了方便，也可以将列表传递给 `attrs.field` 的验证器参数。

   因此，以下两个语句是等效的::

      x = field(validator=attrs.validators.and_(v1, v2, v3))
      x = field(validator=[v1, v2, v3])

.. autofunction:: attrs.validators.or_

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     val: int | list[int] = field(
      ...         validator=attrs.validators.or_(
      ...             attrs.validators.instance_of(int),
      ...             attrs.validators.deep_iterable(attrs.validators.instance_of(int)),
      ...         )
      ...     )
      >>> C(42)
      C(val=42)
      >>> C([1, 2, 3])
      C(val=[1, 2, 3])
      >>> C(val='42')
      Traceback (most recent call last):
         ...
      ValueError: None of (<instance_of validator for type <class 'int'>>, <deep_iterable validator for iterables of <instance_of validator for type <class 'int'>>>) satisfied for value '42'

.. autofunction:: attrs.validators.not_

   例如:

   .. doctest::

      >>> reserved_names = {"id", "time", "source"}
      >>> @define
      ... class Measurement:
      ...     tags = field(
      ...         validator=attrs.validators.deep_mapping(
      ...             key_validator=attrs.validators.not_(
      ...                 attrs.validators.in_(reserved_names),
      ...                 msg="reserved tag key",
      ...             ),
      ...             value_validator=attrs.validators.instance_of((str, int)),
      ...         )
      ...     )
      >>> Measurement(tags={"source": "universe"})
      Traceback (most recent call last):
         ...
      ValueError: ("reserved tag key", Attribute(name='tags', default=NOTHING, validator=<not_ validator wrapping <in_ validator with options {'id', 'time', 'source'}>, capturing (<class 'ValueError'>, <class 'TypeError'>)>, type=None, kw_only=False), <in_ validator with options {'id', 'time', 'source'}>, {'source_': 'universe'}, (<class 'ValueError'>, <class 'TypeError'>))
      >>> Measurement(tags={"source_": "universe"})
      Measurement(tags={'source_': 'universe'})


.. autofunction:: attrs.validators.optional

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(
      ...         validator=attrs.validators.optional(
      ...             attrs.validators.instance_of(int)
      ...         ))
      >>> C(42)
      C(x=42)
      >>> C("42")
      Traceback (most recent call last):
         ...
      TypeError: ("'x' must be <type 'int'> (got '42' that is a <type 'str'>).", Attribute(name='x', default=NOTHING, validator=<instance_of validator for type <type 'int'>>, type=None, kw_only=False), <type 'int'>, '42')
      >>> C(None)
      C(x=None)


.. autofunction:: attrs.validators.is_callable

    例如:

    .. doctest::

        >>> @define
        ... class C:
        ...     x = field(validator=attrs.validators.is_callable())
        >>> C(isinstance)
        C(x=<built-in function isinstance>)
        >>> C("not a callable")
        Traceback (most recent call last):
            ...
        attr.exceptions.NotCallableError: 'x' must be callable (got 'not a callable' that is a <class 'str'>).


.. autofunction:: attrs.validators.matches_re

    例如:

    .. doctest::

        >>> @define
        ... class User:
        ...     email = field(validator=attrs.validators.matches_re(
        ...         r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"))
        >>> User(email="user@example.com")
        User(email='user@example.com')
        >>> User(email="user@example.com@test.com")
        Traceback (most recent call last):
            ...
        ValueError: ("'email' must match regex '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\\\.[a-zA-Z0-9-.]+$)' ('user@example.com@test.com' doesn't)", Attribute(name='email', default=NOTHING, validator=<matches_re validator for pattern re.compile('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)')>, repr=True, cmp=True, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False), re.compile('(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$)'), 'user@example.com@test.com')


.. autofunction:: attrs.validators.deep_iterable

    例如:

    .. doctest::

        >>> @define
        ... class C:
        ...     x = field(validator=attrs.validators.deep_iterable(
        ...             member_validator=attrs.validators.instance_of(int),
        ...             iterable_validator=attrs.validators.instance_of(list)
        ...     ))
        >>> C(x=[1, 2, 3])
        C(x=[1, 2, 3])
        >>> C(x=set([1, 2, 3]))
        Traceback (most recent call last):
            ...
        TypeError: ("'x' must be <class 'list'> (got {1, 2, 3} that is a <class 'set'>).", Attribute(name='x', default=NOTHING, validator=<deep_iterable validator for <instance_of validator for type <class 'list'>> iterables of <instance_of validator for type <class 'int'>>>, repr=True, cmp=True, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False), <class 'list'>, {1, 2, 3})
        >>> C(x=[1, 2, "3"])
        Traceback (most recent call last):
            ...
        TypeError: ("'x' must be <class 'int'> (got '3' that is a <class 'str'>).", Attribute(name='x', default=NOTHING, validator=<deep_iterable validator for <instance_of validator for type <class 'list'>> iterables of <instance_of validator for type <class 'int'>>>, repr=True, cmp=True, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False), <class 'int'>, '3')


.. autofunction:: attrs.validators.deep_mapping

    例如:

    .. doctest::

        >>> @define
        ... class C:
        ...     x = field(validator=attrs.validators.deep_mapping(
        ...             key_validator=attrs.validators.instance_of(str),
        ...             value_validator=attrs.validators.instance_of(int),
        ...             mapping_validator=attrs.validators.instance_of(dict)
        ...     ))
        >>> C(x={"a": 1, "b": 2})
        C(x={'a': 1, 'b': 2})
        >>> C(x=None)
        Traceback (most recent call last):
            ...
        TypeError: ("'x' must be <class 'dict'> (got None that is a <class 'NoneType'>).", Attribute(name='x', default=NOTHING, validator=<deep_mapping validator for objects mapping <instance_of validator for type <class 'str'>> to <instance_of validator for type <class 'int'>>>, repr=True, cmp=True, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False), <class 'dict'>, None)
        >>> C(x={"a": 1.0, "b": 2})
        Traceback (most recent call last):
            ...
        TypeError: ("'x' must be <class 'int'> (got 1.0 that is a <class 'float'>).", Attribute(name='x', default=NOTHING, validator=<deep_mapping validator for objects mapping <instance_of validator for type <class 'str'>> to <instance_of validator for type <class 'int'>>>, repr=True, cmp=True, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False), <class 'int'>, 1.0)
        >>> C(x={"a": 1, 7: 2})
        Traceback (most recent call last):
            ...
        TypeError: ("'x' must be <class 'str'> (got 7 that is a <class 'int'>).", Attribute(name='x', default=NOTHING, validator=<deep_mapping validator for objects mapping <instance_of validator for type <class 'str'>> to <instance_of validator for type <class 'int'>>>, repr=True, cmp=True, hash=None, init=True, metadata=mappingproxy({}), type=None, converter=None, kw_only=False), <class 'str'>, 7)

验证器可以在全局和局部两种情况下禁用：

.. autofunction:: attrs.validators.set_disabled

.. autofunction:: attrs.validators.get_disabled

.. autofunction:: attrs.validators.disabled


Converters
----------

.. autoclass:: attrs.Converter

   例如:

   .. doctest::

      >>> def complicated(value, self_, field):
      ...     return int(value) * self_.factor + field.metadata["offset"]
      >>> @define
      ... class C:
      ...     factor = 5  # not an *attrs* field
      ...     x = field(
      ...         metadata={"offset": 200},
      ...         converter=attrs.Converter(
      ...             complicated,
      ...             takes_self=True, takes_field=True
      ...     ))
      >>> C("42")
      C(x=410)


.. module:: attrs.converters

``attrs.converters`` 中的所有对象也可以从 ``attr.converters`` 访问（这两个命名空间中的模块是相同的）。

.. autofunction:: attrs.converters.pipe

   为了方便，也可以将列表传递给 `attrs.field` / `attr.ib` 的转换器参数。

   因此，以下两个语句是等效的::

      x = attrs.field(converter=attrs.converter.pipe(c1, c2, c3))
      x = attrs.field(converter=[c1, c2, c3])

.. autofunction:: attrs.converters.optional

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(converter=attrs.converters.optional(int))
      >>> C(None)
      C(x=None)
      >>> C(42)
      C(x=42)


.. autofunction:: attrs.converters.default_if_none

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(
      ...         converter=attrs.converters.default_if_none("")
      ...     )
      >>> C(None)
      C(x='')


.. autofunction:: attrs.converters.to_bool(val)

   例如:

   .. doctest::

      >>> @define
      ... class C:
      ...     x = field(
      ...         converter=attrs.converters.to_bool
      ...     )
      >>> C("yes")
      C(x=True)
      >>> C(0)
      C(x=False)
      >>> C("norway")
      Traceback (most recent call last):
         File "<stdin>", line 1, in <module>
      ValueError: Cannot convert value to bool: norway




.. _api_setters:

Setters
-------

.. module:: attrs.setters

这些是您可以与 `attrs.define` 和 `attrs.field` 的 ``on_setattr`` 参数一起使用的助手。
``attrs.setters`` 中的所有设置器也可以从 ``attr.setters`` 访问（它们是在不同命名空间中的相同模块）。

.. autofunction:: frozen
.. autofunction:: validate
.. autofunction:: convert
.. autofunction:: pipe

.. data:: NO_OP

   用于禁用某些属性的类级 *on_setattr* 钩子的哨兵。

   在 `attrs.setters.pipe` 或列表中无效。

   .. versionadded:: 20.1.0

   例如，这里只有 ``x`` 是冻结(frozen)的：

   .. doctest::

     >>> @define(on_setattr=attr.setters.frozen)
     ... class C:
     ...     x = field()
     ...     y = field(on_setattr=attr.setters.NO_OP)
     >>> c = C(1, 2)
     >>> c.y = 3
     >>> c.y
     3
     >>> c.x = 4
     Traceback (most recent call last):
         ...
     attrs.exceptions.FrozenAttributeError: ()

   .. tip::
      使用 `attrs.define` 的 *frozen* 参数（或 `attrs.frozen`）来冻结整个类；这样更有效。
