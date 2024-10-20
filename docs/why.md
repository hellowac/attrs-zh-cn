# 为什么不用……

如果你想了解第三方对 *attrs* 优点的看法，可以看看 Glyph 的 [*The One Python Library Everyone Needs*](https://glyph.twistedmatrix.com/2016/08/attrs.html)。
它的出现早于类型注解和数据类，但它巧妙地说明了类构建库的吸引力。


## ……数据类？

{pep}`557` 在 [Python 3.7](https://docs.python.org/3.7/whatsnew/3.7.html#dataclasses) 中添加了数据类，它们在许多方面与 *attrs* 相似。

它们是 Python 社区[希望](https://mail.python.org/pipermail/python-ideas/2017-May/045618.html)能在标准库中拥有一种比 `namedtuple` 更简单的类写法的产物。
为此，*attrs* 及其开发者参与了 PEP 过程，虽然我们对其中一些小决定持不同意见，但它依然是一个不错的库，如果它能阻止你滥用 `namedtuple`，那无疑是一个巨大胜利。

尽管如此，仍然有理由选择 *attrs* 而非数据类。它们是否与*你*相关取决于你的情况：

- 数据类*故意*比 *attrs* 功能少。为了简化，许多功能被牺牲了，最明显的是验证器、转换器、[自定义相等性](custom-comparison)、[`__init_subclass__` 问题的解决方案](init-subclass)或 {doc}`扩展性 <extending>`等功能——这种简化贯穿了所有 API。

  另一方面，数据类目前没有提供 *attrs* 已经不具备的任何重要功能。

- 我们更愿意不惜代价去实现那些复杂但合理的功能。

  这包括通过调试器逐步执行生成的方法、进行单元重写以使裸 `super()` 调用正常工作，或在 slotted 类上使 {func}`functools.cached_property` 正常工作。

- *attrs* 支持所有主流 Python 版本，包括 PyPy。

- 如果你不喜欢类型注解，*attrs* 不会强迫你使用它们。

- 但因为它**也**支持类型提示，因此也是逐步接受类型提示的最佳方式。

- 尽管数据类偶尔会实现一些 *attrs* 的功能，但它们的实现与 Python 版本相关，而非包的版本。
  例如，对 `__slots__` 的支持仅在 Python 3.10 中添加，但它不进行单元重写，因此不支持裸 `super()` 调用。

  这可能会在后续的 Python 版本中修复，但处理这些差异对支持多个 Python 版本的 PyPI 包尤其痛苦。
  当然，这也包括可能存在的实现错误。

- *attrs* 可以并且将会更快地发展。
  我们不受任何发布计划的约束，并且有明确的弃用政策。

  不将 *attrs* 包含在标准库中的[原因之一](https://peps.python.org/pep-0557/#why-not-just-use-attrs)是为了不妨碍 *attrs* 的未来发展。

可以这样看待 *attrs* 与数据类的区别：*attrs* 是一个功能齐全的工具包，用于编写强大的类，而数据类则是获得带有一些属性的类的简便方法。
基本上相当于 2015 年的 *attrs*。


## ……Pydantic？

Pydantic 首先是一个*数据验证与类型强制库*。
因此，它是类构建库（如 *attrs* 或数据类）的有力补充，用于解析和验证不受信任的数据。

然而，尽管它可能很方便，但将其用于你的业务或数据层[在多个方面是有问题的](https://threeofwands.com/why-i-use-attrs-instead-of-pydantic/)：
是否真的有必要在从受信任的数据库中读取对象时重新验证所有对象？
你的 Web API 的结构是否应该对你的业务对象（从而是业务代码）施加设计压力？

按照 [*表单、命令和模型验证*](https://verraes.net/2015/02/form-command-model-validation/)的说法，Pydantic 是适用于*命令*的正确工具。

[*关注点分离*](https://en.wikipedia.org/wiki/Separation_of_concerns) 有时可能显得繁琐，但它是一种你会在犯了足够多的错误后逐渐欣赏的设计原则，尤其当你看到允许来自系统边缘（如 ORM 或 Web API）的设计压力的结果时。

*attrs* 明确**不会**尝试成为一个验证库，而是一个工具包，用于编写像你自己会编写的良好行为类。
如果你想要一个强大的库用于结构化、去结构化和验证数据，可以看看 [*cattrs*](https://catt.rs/)，它是 *attrs* 家族的正式成员。
它的核心原则之一是它不将你的类与外部因素耦合。


## ……namedtuple？

{obj}`collections.namedtuple` 是带名字的元组，而不是类。[^history]
由于在 Python 中编写类比较繁琐，时不时有人发现他们可以节省大量的输入操作，结果对此感到非常兴奋。
然而，这种方便是有代价的。

`namedtuple` 和基于 *attrs* 的类之间最明显的区别在于后者是类型敏感的：

```{doctest}
>>> import attrs
>>> C1 = attrs.make_class("C1", ["a"])
>>> C2 = attrs.make_class("C2", ["a"])
>>> i1 = C1(1)
>>> i2 = C2(1)
>>> i1.a == i2.a
True
>>> i1 == i2
False
```

……而 `namedtuple` *故意* [表现得像个元组](https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences)，这意味着元组的类型*被忽略*：

```{doctest}
>>> from collections import namedtuple
>>> NT1 = namedtuple("NT1", "a")
>>> NT2 = namedtuple("NT2", "b")
>>> t1 = NT1(1)
>>> t2 = NT2(1)
>>> t1 == t2 == (1,)
True
```

其他经常令人意外的行为包括：

- 由于它们是元组的子类，`namedtuple` 有长度，并且既可迭代又可索引。
  这不是你对类的期望，可能会掩盖一些微妙的拼写错误。

- 可迭代性还意味着 `namedtuple` 容易被意外解包，这会导致难以发现的错误。[^iter]

- 无论你是否喜欢，`namedtuple` 的方法都会在你的实例上存在。[^pollution]

- `namedtuple` 始终*不可变*。
  这不仅意味着你不能自行决定实例是否不可变，还意味着如果你想要影响类的初始化（验证？默认值？），你必须实现 {meth}`__new__() <object.__new__>`，这是一个特别棘手且容易出错的解决方案，对于一个非常常见的问题来说尤为如此。[^immutable]

- 如果要为 `namedtuple` 添加方法，你必须对其进行子类化。
  如果你按照标准库文档的建议：

  ```
  class Point(namedtuple('Point', ['x', 'y'])):
      # ...
  ```

  你最终会得到一个在 {attr}`__mro__ <type.__mro__>` 中包含*两个* `Point` 的类：`[<class 'point.Point'>, <class 'point.Point'>, <type 'tuple'>, <type 'object'>]`。

  这不仅令人困惑，还会产生非常实际的影响：
  例如，如果你创建包含类层次结构的文档（如 [*Sphinx* 的 autodoc](https://www.sphinx-doc.org/en/stable/usage/extensions/autodoc.html) 并显示继承关系），会带来混乱。
  再次强调：常见问题，方案笨拙且后果令人困惑。

所有这些都使得 `namedtuple` 对公共 API 来说是一个特别糟糕的选择，因为所有的对象都不可挽回地被污染了。
使用 *attrs*，你的用户不会注意到任何区别，因为它创建的是常规的、良好行为的类。

:::{admonition} 总结
如果你只想要一个*带名字的元组*，那么尽管使用 `namedtuple` 吧。[^perf]
但如果你想要一个带有方法的类，依赖于一堆需要更多 hack 才能应对扩展需求的 hack 只会给自己带来麻烦。

除此之外，*attrs* 还添加了一些方便的功能，如验证器、转换器和（可变的！）默认值。
:::

[^history]: 据说 `namedtuple` 被添加到 Python 标准库中，是为了让返回值中的元组更加可读。
    确实，你可以在整个标准库中看到这种使用。

    看看 `namedtuple` 的创造者自己是如何使用它的，这对你决定自己的使用场景是一个很好的指南。

[^pollution]: *attrs* 只添加了一个属性：`__attrs_attrs__`，用于自省。
    所有辅助函数都在 `attr` 包中。
    由于它们以实例作为第一个参数，你可以轻松地将它们附加到自己的类中，并为其指定自己的名称。

[^iter]: {func}`attrs.astuple` 可用于在 *attrs* 中*按需显式*获取此行为。

[^immutable]: *attrs* 通过 `frozen` 关键字提供*可选*的不可变性。

[^perf]: 虽然 *attrs* 也能很好地胜任！
    由于两者都采用为你编写和编译 Python 代码的方法，性能差异在最坏的情况下是可以忽略的，在某些情况下，如果你使用 `slots=True`（这通常是个好主意），*attrs* 甚至更快。


## … tuples?

### 可读性

调试时，哪个更清晰：

```
Point(x=1, y=2)
```

还是：

```
(1, 2)
```

？

让我们增加一些歧义：

```
Customer(id=42, reseller=23, first_name="Jane", last_name="John")
```

还是：

```
(42, 23, "Jane", "John")
```

？

为什么你要写 `customer[2]` 而不是 `customer.first_name`？

当你还涉及嵌套时，问题就更复杂了。
如果你调试时从未遇到过那些让人摸不着头脑的神秘元组，那你肯定比我聪明得多。

使用具有名称和类型的合适类，使程序代码更加易读且[易于理解](https://arxiv.org/pdf/1304.5257.pdf)。
尤其是在试图理解一段新软件时，或者几个月后重新查看旧代码时。


### 可扩展性

假设你有一个接受或返回元组的函数。
尤其是在你使用元组解包（如 `x, y = get_point()`）的情况下，添加额外的数据意味着你必须在*所有地方*更改该函数的调用方式。

而向类中添加一个属性只会影响那些真正关心该属性的人。


## …… 字典？

字典不适用于固定字段。

如果你有一个字典，它应该将某物映射到其他东西。
你应该可以随意添加或删除值。

*attrs* 让你可以明确这些预期；字典则不能。
它在代码中为你提供了一个带有名称的实体（类），这让你可以在其他地方说明你是接受该类的参数，还是返回该类的值。

换句话说：如果你的字典有一个固定且已知的键集，那么它就是一个对象，而不是一个哈希表。
因此，如果你从未遍历字典的键，那么你应该使用合适的类。


## …… 手写类？

虽然我们很喜欢手工制作的东西，但一遍又一遍地写同样的九个方法不太算在内。我通常会不小心打错字，而且有更多的代码可能会出错，因此需要测试。

为了更直观地比较，相当于以下代码：

```{doctest}
>>> @attrs.define
... class SmartClass:
...    a = attrs.field()
...    b = attrs.field()
>>> SmartClass(1, 2)
SmartClass(a=1, b=2)
```

手写类的大致代码如下：

```{doctest}
>>> class ArtisanalClass:
...     def __init__(self, a, b):
...         self.a = a
...         self.b = b
...
...     def __repr__(self):
...         return f"ArtisanalClass(a={self.a}, b={self.b})"
...
...     def __eq__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) == (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __ne__(self, other):
...         result = self.__eq__(other)
...         if result is NotImplemented:
...             return NotImplemented
...         else:
...             return not result
...
...     def __lt__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) < (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __le__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) <= (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __gt__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) > (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __ge__(self, other):
...         if other.__class__ is self.__class__:
...             return (self.a, self.b) >= (other.a, other.b)
...         else:
...             return NotImplemented
...
...     def __hash__(self):
...         return hash((self.__class__, self.a, self.b))
>>> ArtisanalClass(a=1, b=2)
ArtisanalClass(a=1, b=2)
```

这段代码相当冗长，甚至还没使用 *attrs* 的高级功能，比如验证器或默认值。此外：完全没有任何测试。而且，谁能保证你在第十次实现 `__gt__` 时不会不小心把 `<` 反转过来？

还需要注意的是，*attrs* 并不是一个全有或全无的解决方案。你可以自由选择想要的功能，并禁用那些你希望自己控制的部分：

```{doctest}
>>> @attrs.define
... class SmartClass:
...    a: int
...    b: int
...
...    def __repr__(self):
...        return f"<SmartClass(a={self.a})>"
>>> SmartClass(1, 2)
<SmartClass(a=1)>
```

:::{admonition} 总结
如果你不介意大量的重复打字，我们不会阻止你。

然而，考虑到在手写类中很难找到关键部分，并且保证在所有类中正确地复制粘贴代码是多么麻烦，声称 *attrs* 增加了项目的心智负担，需要很大的偏见和决心来合理化这一点。

无论如何，如果你有一天厌倦了重复性的工作和淹没在大量样板代码中的重要逻辑，*attrs* 将会在此等候你。
:::
