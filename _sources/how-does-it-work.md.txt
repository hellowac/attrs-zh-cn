(how)=

# 它是如何工作的？(How Does It Work?)

## 样板(Boilerplate)

*attrs* 不是第一个旨在简化 Python 类定义的库。
但其 **声明式** 方法结合 **无运行时开销** 的特点使其独树一帜。

一旦你将 `@attrs.define`（或 `@attr.s`）装饰器应用于一个类，*attrs* 会在类对象中搜索 `attr.ib` 的实例。
它们在内部是传递给 `attr.ib` 的数据的表示，带有一个计数器以保持属性的顺序。
另外，也可以使用 {doc}`types` 来定义它们。

为了确保子类化按预期工作，*attrs* 还会遍历类层次结构，收集所有基类的属性。
请注意，*attrs* **不会** 调用 `super()`。
它会编写 {term}`双下划线方法 <dunder methods>` 来处理 **所有** 这些属性，这也带来了由于减少函数调用而提高的性能。

一旦 *attrs* 知道它需要处理哪些属性，它就会写入请求的 {term}`双下划线方法 <dunder methods>`，并根据你希望创建的是 {term}`dict <dict classes>` 还是 {term}`slotted <slotted classes>` 类，创建一个新类（`slots=True`）或将它们附加到原始类（`slots=False`）。
虽然创建新类更优雅，但我们遇到了一些围绕元类的边缘情况，使得无法无条件地走这条路。

明确一点：如果你定义一个只有一个没有默认值的属性的类，生成的 `__init__` 将看起来 *完全* 如你所预期：

```{doctest}
>>> import inspect
>>> from attrs import define
>>> @define
... class C:
...     x: int
>>> print(inspect.getsource(C.__init__))
def __init__(self, x):
    self.x = x
<BLANKLINE>
```

没有魔法，没有元编程，没有昂贵的运行时反射。

---

直到这一点为止，所有的操作都是在类定义时 **一次性** 完成的。
一旦一个类定义完成，它就完成了。
它只是一个常规的 Python 类，除了有一个 `__attrs_attrs__` 属性，*attrs* 在内部使用。
很多信息可以通过 {func}`attrs.fields` 和其他函数访问，这些函数可用于反射或为 *attrs* 编写你自己的工具和装饰器（如 {func}`attrs.asdict`）。

一旦你开始实例化你的类，*attrs* 就完全不再干预。

这种 **静态** 方法是 *attrs* 的一个设计目标，我坚信这使其与众不同。

(how-frozen)=

## 不可变性(Immutability)

为了实现不可变性，*attrs* 将在你的类上附加一个 `__setattr__` 方法，当任何人尝试设置属性时，将抛出 {class}`attrs.exceptions.FrozenInstanceError`。

如果你选择使用 {obj}`attrs.setters.frozen` *on_setattr* 钩子来冻结单个属性，则异常将变为 {class}`attrs.exceptions.FrozenAttributeError`。

这两个异常都继承自 {class}`attrs.exceptions.FrozenError`。

---

根据类是字典类还是插槽类，*attrs* 使用不同的技术来绕过 `__init__` 方法中的限制。

一旦构造完成，冻结的实例与常规实例没有任何不同，除了你无法更改其属性。


### 字典类(Dict Classes)

字典类——即：常规类——直接将值分配到类的同名 `__dict__` 中（我们无法阻止用户这样做）。

性能影响可以忽略不计。


### 插槽类(Slotted Classes)

插槽类则更复杂。
它使用（一个激进缓存的）{meth}`object.__setattr__` 来设置你的属性。
这（仍然）比普通赋值慢：

```none
$ pyperf timeit --rigorous \
      -s "import attr; C = attr.make_class('C', ['x', 'y', 'z'], slots=True)" \
      "C(1, 2, 3)"
.........................................
Mean +- std dev: 228 ns +- 18 ns

$ pyperf timeit --rigorous \
      -s "import attr; C = attr.make_class('C', ['x', 'y', 'z'], slots=True, frozen=True)" \
      "C(1, 2, 3)"
.........................................
Mean +- std dev: 425 ns +- 16 ns
```

因此，在一台笔记本电脑上，差异约为 200 纳秒（1 秒为 1,000,000,000 纳秒）。
在热循环中你肯定会感受到这个差异，但在正常代码中不应该有太大问题。
根据你的需求选择更重要的方面。

### 总结(Summary)

在性能关键代码中，你应避免实例化大量冻结的插槽类（即：`@frozen`）。

冻结的字典类几乎没有性能影响，未冻结的插槽类甚至比未冻结的字典类（即：常规类）还要快。


(how-slotted-cached_property)=

## 插槽类中被缓存的属性(Cached Properties on Slotted Classes)

默认情况下，标准库的 {func}`functools.cached_property` 装饰器无法在插槽类上使用，因为它需要一个 `__dict__` 来存储缓存值。
这可能会让使用 *attrs* 的用户感到意外，因为插槽类是默认设置。
因此，*attrs* 在构造插槽类时会转换 `cached_property` 装饰的方法。

实现这一功能的方式包括：

* 为被包装的方法添加名称到 `__slots__` 中。
* 添加一个 `__getattr__` 方法以设置被包装方法的值。

对于大多数用户来说，这意味着它可以透明地工作。

:::{note}
该实现并不保证在多线程使用中被包装的方法仅调用一次。这与 Python 3.12 中 `cached_property` 的实现相匹配。
:::
