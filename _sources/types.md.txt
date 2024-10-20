# 类型注解

*attrs* 对 {pep}`526` 和旧语法的类型注解提供了第一类支持。

然而，它们将永远保持 *可选(optional)*，因此来自 README 的示例也可以写成：

```{doctest}
>>> from attrs import define, field

>>> @define
... class SomeClass:
...     a_number = field(default=42)
...     list_of_numbers = field(factory=list)

>>> sc = SomeClass(1, [1, 2, 3])
>>> sc
SomeClass(a_number=1, list_of_numbers=[1, 2, 3])
```

您可以自由选择这两种方法，但请记住，如果您选择使用类型注解，您 **必须** 注解 **所有** 属性！

:::{caution}
如果您定义一个 {func}`attrs.field` 但 **缺少** 类型注解的类，*attrs* 将 **忽略** 其他已经有类型注解但未使用 {func}`attrs.field` 定义的字段：

```{doctest}
>>> @define
... class SomeClass:
...     a_number = field(default=42)
...     another_number: int = 23
>>> SomeClass()
SomeClass(a_number=42)
```
:::

即使在全面使用类型注解的情况下，某些高级特性仍然需要 {func}`attrs.field`。

这些特性之一是基于装饰器的功能，例如默认值。
重要的是要记住，*attrs* 不会在您背后做任何魔法。
所有装饰器都是使用对 {func}`attrs.field` 调用返回的对象实现的。

仅携带类注解的属性没有该对象，因此尝试对其调用方法将不可避免地失败。

---

请注意，无论如何添加，类型仅是可从类查询的 *元数据(metadata)*，并且在开箱即用的情况下不用于任何其他用途！

由于 Python 不允许在类定义之前引用类对象，因此类型可以定义为字符串字面量，即所谓的 *前向引用* ({pep}`526`)。
您可以通过使用 `from __future__ import annotations` ({pep}`563`) 自动为整个模块启用此功能。
在这种情况下，*attrs* 只是将这些字符串字面量放入 `type` 属性中。
如果您需要将它们解析为真实类型，可以调用 {func}`attrs.resolve_types`，该方法将就地更新属性。

然而，在实践中，类型在与像 [Mypy]、[*pytype*] 或 [Pyright] 这样的工具结合使用时显示出最大的实用性，这些工具对 *attrs* 类提供了专门支持。

静态类型的增加无疑是 Python 生态系统中最令人兴奋的功能之一，并帮助您编写 *正确的(correct)* 和 *经过验证的自我文档(verified self-documenting)* 代码。


## Mypy

虽然有一个漂亮的类型元数据语法是很好的，但更棒的是 [Mypy] 提供了一个专门的 *attrs* 插件，可以让您静态检查代码。

想象一下，您添加了一行代码，尝试使用 `SomeClass("23")` 实例化定义的类。
Mypy 会为您捕获该错误：

```console
$ mypy t.py
t.py:12: error: Argument 1 to "SomeClass" has incompatible type "str"; expected "int"
```

这一切都发生在 *不运行* 您的代码的情况下！

它还适用于 *两种* 旧的注解样式。
对 Mypy 而言，这段代码与上面的代码等效：

```python
@attr.s
class SomeClass:
    a_number = attr.ib(default=42)  # type: int
    list_of_numbers = attr.ib(factory=list, type=list[int])
```

`list_of_numbers` 的这种方法仅在我们的 [旧式 API](names.md) 中可用，这就是示例仍然使用它的原因。

## Pyright

*attrs* 通过 `dataclass_transform` / {pep}`681` 规范提供对 [Pyright] 的支持。
这为一部分 *attrs* 提供了静态类型推断，相当于标准库中的 {mod}`dataclasses`，
并需要使用 {func}`attrs.define` 或 `@attr.s(auto_attribs=True)` API 进行显式类型注解。

给定以下定义，Pyright 将为 `SomeClass` 的属性访问、`__init__`、`__eq__` 和比较方法生成静态类型签名：

```
@attrs.define
class SomeClass:
    a_number: int = 42
    list_of_numbers: list[int] = attr.field(factory=list)
```

:::{warning}
Pyright 推断的类型是支持的类型的一个小子集，包括：

- `attrs.frozen` 装饰器没有与冻结属性进行类型注解，而这些属性可以通过 `attrs.define(frozen=True)` 进行正确的类型注解。

我们欢迎您对 [attrs#795](https://github.com/python-attrs/attrs/issues/795) 和 [pyright#1782](https://github.com/microsoft/pyright/discussions/1782) 提出建设性反馈。
一般来说，改善 Pyright 中 *attrs* 支持的决定完全取决于微软，他们明确表示将仅添加经过 PEP 过程的功能支持。
:::


## 类变量和常量

如果您正在为所有代码添加类型注解，您可能会想知道如何定义类变量（与实例变量相对），因为在类作用域中赋值的值会成为该属性的默认值。
然而，正确的方式是使用 {data}`typing.ClassVar` 来类型注解这样的类变量，这表明该变量应仅在类（或其子类）中进行赋值，而不是在类的实例中。
*attrs* 将跳过注解为 {data}`typing.ClassVar` 的成员，允许您编写类型注解，而不会将该成员变成属性。
类变量通常用于常量，但也可以用于在类的所有实例之间共享的可变单例数据。

```python
@attrs.define
class PngHeader:
    SIGNATURE: typing.ClassVar[bytes] = b'\x89PNG\r\n\x1a\n'
    height: int
    width: int
    interlaced: int = 0
    ...
```

[Mypy]: http://mypy-lang.org
[Pyright]: https://github.com/microsoft/pyright
[*pytype*]: https://google.github.io/pytype/
