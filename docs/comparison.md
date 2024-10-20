# 比较(Comparison)

默认情况下，两个 *attrs* 类的实例如果具有相同的类型且所有字段相等，则被视为相等。为此，*attrs* 会为您编写 `__eq__` 和 `__ne__` 方法。

此外，如果您传递 `order=True`，*attrs* 还会创建一整套排序方法：`__le__`、`__lt__`、`__ge__` 和 `__gt__`。

在进行相等性比较时，*attrs* 将生成一个语句，比较两个实例的类型，然后逐个比较每个属性，使用 `==`。

在进行排序时，*attrs* 将：

- 检查您正在比较的实例的类型是否相等，
- 如果相等，为每个实例创建一个包含所有字段值的元组，
- 最后对这些元组执行所需的比较操作。

(custom-comparison)=

## 自定义(Customization)

与其他功能一样，您可以排除字段参与比较操作：

```{doctest}
>>> from attrs import define, field
>>> @define
... class C:
...     x: int
...     y: int = field(eq=False)

>>> C(1, 2) == C(1, 3)
True
```

此外，您还可以向 *eq* 和 *order* 传递一个 *可调用对象* 而不是布尔值。然后，它将被用作键函数，就像您在 {func}`sorted` 中可能知道的那样：

```{doctest}
>>> @define
... class S:
...     x: str = field(eq=str.lower)

>>> S("foo") == S("FOO")
True

>>> @define(order=True)
... class C:
...     x: str = field(order=int)

>>> C("10") > C("2")
True
```

当您有具有不典型比较属性的对象字段时，这尤其有用。此类对象的常见示例是 [NumPy 数组](https://github.com/python-attrs/attrs/issues/435)。

为了让您避免不必要的样板代码，*attrs* 提供了 {func}`attrs.cmp_using` 帮助器来创建这样的函数。对于 NumPy 数组，它看起来像这样：

```python
import numpy

@define
class C:
   an_array = field(eq=attrs.cmp_using(eq=numpy.array_equal))
```

:::{warning}
请注意，*eq* 和 *order* 是 *独立设置* 的，因为在 {func}`~attrs.define` 中 *order* 默认为 `False`（但在 {func}`attr.s` 中不是）。您可以通过使用我们刚刚为此用例重新引入的 *cmp* 参数来同时设置两者。
:::
