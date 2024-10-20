``attr`` 命名空间API参考
========================================

.. note::

   这些是传统的 API，其创建早于类型注解。它们 **不是** 被弃用，但我们建议在新代码中使用 :mod:`attrs` 命名空间，因为它们看起来更美观，且具有更好的默认值。

   同样参见 :doc:`names`.

.. module:: attr


核心(Core)
------------

.. autofunction:: attr.s(these=None, repr_ns=None, repr=None, cmp=None, hash=None, init=None, slots=False, frozen=False, weakref_slot=True, str=False, auto_attribs=False, kw_only=False, cache_hash=False, auto_exc=False, eq=None, order=None, auto_detect=False, collect_by_mro=False, getstate_setstate=None, on_setattr=None, field_transformer=None, match_args=True, unsafe_hash=None)

   例如:

   .. doctest::

      >>> import attr
      >>> @attr.s
      ... class C:
      ...     _private = attr.ib()
      >>> C(private=42)
      C(_private=42)
      >>> class D:
      ...     def __init__(self, x):
      ...         self.x = x
      >>> D(1)
      <D object at ...>
      >>> D = attr.s(these={"x": attr.ib()}, init=False)(D)
      >>> D(1)
      D(x=1)
      >>> @attr.s(auto_exc=True)
      ... class Error(Exception):
      ...     x = attr.ib()
      ...     y = attr.ib(default=42, init=False)
      >>> Error("foo")
      Error(x='foo', y=42)
      >>> raise Error("foo")
      Traceback (most recent call last):
         ...
      Error: ('foo', 42)
      >>> raise ValueError("foo", 42)   # for comparison
      Traceback (most recent call last):
         ...
      ValueError: ('foo', 42)


.. autofunction:: attr.ib

   .. note::

      *attrs* 还附带一个重要别名 ``attr.attrib`` 。

   `attr.ib` 返回的对象还允许使用装饰器设置默认值和验证器：

   .. doctest::

      >>> @attr.s
      ... class C:
      ...     x = attr.ib()
      ...     y = attr.ib()
      ...     @x.validator
      ...     def _any_name_except_a_name_of_an_attribute(self, attribute, value):
      ...         if value < 0:
      ...             raise ValueError("x must be positive")
      ...     @y.default
      ...     def _any_name_except_a_name_of_an_attribute(self):
      ...         return self.x + 1
      >>> C(1)
      C(x=1, y=2)
      >>> C(-1)
      Traceback (most recent call last):
          ...
      ValueError: x must be positive

.. function:: attrs

   `attr.s` 的严肃业务别名。

.. function:: define

   与 `attrs.define` 一样.

.. function:: mutable

   与 `attrs.mutable` 一样.

.. function:: frozen

   与 `attrs.frozen` 一样.

.. function:: field

   与 `attrs.field` 一样.

.. class:: Attribute

   与 `attrs.Attribute` 一样.

.. function:: make_class

   与 `attrs.make_class` 一样.

.. autoclass:: Factory
   :noindex:

   与 `attrs.Factory` 一样.


.. data:: NOTHING

   与 `attrs.NOTHING` 一样.


Exceptions
----------

.. module:: attr.exceptions

所有异常都可以从 ``attr.exceptions`` 和 `attrs.exceptions` 获得（它们是不同命名空间中的相同模块）。

请参阅 `attrs.exceptions` 了解详情。


Helpers
-------

.. currentmodule:: attr

.. function:: cmp_using

   与 `attrs.cmp_using` 一样.

.. function:: fields

   与 `attrs.fields` 一样.

.. function:: fields_dict

   与 `attrs.fields_dict` 一样.

.. function:: has

   与 `attrs.has` 一样.

.. function:: resolve_types

   与 `attrs.resolve_types` 一样.

.. autofunction:: asdict
.. autofunction:: astuple

.. module:: attr.filters

.. function:: include

   与 `attrs.filters.include` 一样.

.. function:: exclude

   与 `attrs.filters.exclude` 一样.

参见 :func:`attrs.asdict` 查看更多示例.

``attr.filters`` 中的所有对象也可在 `attrs.filters` 中使用。

----

.. currentmodule:: attr

.. function:: evolve

   与 `attrs.evolve` 一样.

.. function:: validate

   与 `attrs.validate` 一样.


Validators
----------

.. module:: attr.validators

所有来自 `attrs.validators` 的对象也可以在 ``attr.validators`` 中找到。详情请参阅前者。


Converters
----------

.. module:: attr.converters

所有来自 `attrs.converters` 的对象也可以从 ``attr.converters`` 获得。请参阅前者了解详情。


Setters
-------

.. module:: attr.setters

所有来自 `attrs.setters` 的对象也可以在 ``attr.setters`` 中使用。请参阅前者以了解详情。


Deprecated APIs
---------------

.. currentmodule:: attr

为了帮助您编写向后兼容的代码，在现代版本中不会引发警告， ``attr`` 模块自 19.2.0 版本起提供了一个 ``__version_info__`` 属性。
它的行为类似于 `sys.version_info` ，并且是 `attr.VersionInfo` 的一个实例：

.. autoclass:: VersionInfo

   在它的帮助下，您可以编写如下代码：

   >>> if getattr(attr, "__version_info__", (0,)) >= (19, 2):
   ...     cmp_off = {"eq": False}
   ... else:
   ...     cmp_off = {"cmp": False}
   >>> cmp_off == {"eq":  False}
   True
   >>> @attr.s(**cmp_off)
   ... class C:
   ...     pass


----

.. autofunction:: assoc

在 *attrs* 获得 `attrs.validators.set_disabled` 和 `attrs.validators.get_disabled` 之前，它有以下 API 用于全局启用和禁用验证器。
这些 API 不会被移除，但不推荐使用：

.. autofunction:: set_run_validators
.. autofunction:: get_run_validators

----

以前，严肃的别名被称为 ``attr.attributes`` 和 ``attr.attr``。
虽然没有计划移除它们，但不应在新代码中使用。
