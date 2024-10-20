# 术语(Glossary)

:::{glossary}
dunder methods
  双下划线方法

  "Dunder" 是 "double underscore" 的缩写。

  它是像 `__init__` 或 `__eq__` 这样的函数，有时也被称为 *魔法方法(magic methods)*，或者说它们实现了 *对象协议(object protocol)*。

  在口语中，你可以将 `__init__` 叫作 "dunder init"。

  其首次文档记录使用是在 2002 年 Mark Jackson 在 [邮件列表发布](https://mail.python.org/pipermail/python-list/2002-September/155836.html) 中。


dict classes
  dict 类

  这是一个常规类，其属性存储在每个实例的 {attr}`object.__dict__` 属性中。
  对于具有非常少数据属性的对象来说，这种做法相当浪费，当创建大量实例时，空间消耗可能会变得显著。

  这是使用 *attrs* 和不使用 *attrs* 时默认获得的类类型（除了下一个 API {func}`attrs.define()`、[`attrs.mutable()`](attrs.mutable) 和 [`attrs.frozen()`](attrs.frozen)）。


slotted classes
  slotted 类

  这是一个类，其实例没有 {attr}`object.__dict__` 属性，而是通过 `object.__slots__` 属性定义它们的属性。
  在 *attrs* 中，通过将 `slots=True` 传递给 `@attr.s` 创建这些类（在 {func}`attrs.define()`、[`attrs.mutable()`](attrs.mutable) 和 [`attrs.frozen()`](attrs.frozen) 中默认启用）。

  它们的主要优势是，在 CPython[^pypy] 上使用更少的内存，并且速度稍快。

  但是，它们也带来了一些可能令人惊讶的问题：

  - slotted 类不允许设置除类的 `__slots__` 中定义的任何其他属性：

    ```{doctest}
    >>> from attr import define
    >>> @define
    ... class Coordinates:
    ...     x: int
    ...     y: int
    ...
    >>> c = Coordinates(x=1, y=2)
    >>> c.z = 3
    Traceback (most recent call last):
        ...
    AttributeError: 'Coordinates' object has no attribute 'z'
    ```

  - slotted 类可以像非 slotted 类一样继承其他类，但如果这样做，将失去一些 slotted 类的好处。
    如果必须继承其他类，尽量只从其他 slotted 类继承。

  - 然而，[不可能](https://docs.python.org/3/reference/datamodel.html#slots) 从多个具有 `__slots__` 属性的类继承（你会得到 `TypeError: multiple bases have instance lay-out conflict`）。

  - 在 slotted 类上不可能进行猴子补丁。
    这在测试代码中可能感觉受限，但通常需要对自己的类进行猴子补丁是设计上的问题。

    如果确实需要在测试中猴子补丁一个实例，但又不想在生产代码中放弃 slotted 类的优势，可以始终将 slotted 类作为无进一步更改的字典类进行子类化，从而消除所有限制：

    ```{doctest}
    >>> import unittest.mock
    >>> @define
    ... class Slotted:
    ...     x: int
    ...
    ...     def method(self):
    ...         return self.x
    >>> s = Slotted(42)
    >>> s.method()
    42
    >>> with unittest.mock.patch.object(s, "method", return_value=23):
    ...     pass
    Traceback (most recent call last):
      ...
    AttributeError: 'Slotted' object attribute 'method' is read-only
    >>> @define(slots=False)
    ... class Dicted(Slotted):
    ...     pass
    >>> d = Dicted(42)
    >>> d.method()
    42
    >>> with unittest.mock.patch.object(d, "method", return_value=23):
    ...     assert 23 == d.method()
    ```

  - slotted 类必须实现 {meth}`__getstate__ <object.__getstate__>` 和 {meth}`__setstate__ <object.__setstate__>` 以便使用 {mod}`pickle` 协议 0 和 1 进行序列化。
    因此，*attrs* 会自动为 slotted 类创建这些方法。

    :::{note}
    当使用 `@attr.s(slots=True)` 装饰并且类已经实现了 {meth}`__getstate__ <object.__getstate__>` 和 {meth}`__setstate__ <object.__setstate__>` 方法时，默认情况下，它们将被 *attrs* 自动生成的实现覆盖。

    可以通过设置 `@attr.s(getstate_setstate=False)` 或 `@attr.s(auto_detect=True)` 来避免这种情况。

    {func}`~attrs.define` 默认将 `auto_detect=True` 设置。
    :::

    此外，在使用 {mod}`pickle` 之前，[请三思](https://www.youtube.com/watch?v=7KnfGDajDQw)。

  - slotted 类默认可被弱引用。
    在 CPython 中可以通过将 `weakref_slot=False` 传递给 `@attr.s` 来禁用此功能 [^pypyweakref]。

  - 由于当前不可能在类创建后使其成为 slotted，*attrs* 必须用新类替换你的类。
    尽管它会尽量做到优雅，但某些 metaclass 特性，如 {meth}`object.__init_subclass__` 在 slotted 类中不起作用。

  - {attr}`type.__subclasses__` 属性需要进行垃圾回收（可以使用 {func}`gc.collect` 手动触发），以便原始类被移除。
    有关更多细节，请参见问题 [#407](https://github.com/python-attrs/attrs/issues/407)。

  - 如果定义一个缺少属性的类，slotted 类的 pickle 将失败。

    如果定义了一个 `attrs.field(init=False)` 且在序列化之前没有手动设置该属性，就会发生这种情况。


field
  字段
  
  正如项目名称所暗示的，*attrs* 完全专注于属性。
  我们特别强调，我们只关心属性，而不是类本身——因为我们相信类属于用户。

  这解释了为什么传统 API 使用 {func}`attr.ib`（或 ``attrib``）函数来定义属性，并且我们在整个文档中仍然使用这个术语。

  然而，随着 {mod}`dataclasses`、[Pydantic](https://docs.pydantic.dev/latest/concepts/fields/) 和其他库的出现，“field” 一词已成为 Python 生态系统中类上预定义属性的通用术语。

  因此，在我们的新 API 中，我们也接受了这个术语，通过调用函数 {func}`attrs.field` 来创建它们，并在整个文档中交替使用“field”一词。

  另请参见 {doc}`names`。

attribute
  见 {term}`field`.
:::

[^pypy]: On PyPy, there is no memory advantage in using slotted classes.

[^pypyweakref]: On PyPy, slotted classes are naturally weak-referenceable so `weakref_slot=False` has no effect.
