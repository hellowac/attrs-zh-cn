# 核心API中的名称(On The Core API Names)

你可能会对使用 {func}`attrs.define` 创建 *attrs* 类并带有类型注解字段感到惊讶，而不是使用 {func}`attr.s` 和 {func}`attr.ib()`。

或者，你可能会想知道为什么网络和讲座中充满了这个奇怪的 `attr.s` 和 `attr.ib` -- 包括一些人对此有强烈的看法，并使用 `attr.attrs` 和 `attr.attrib`。

那么，什么是未记录但常用的 `attr.dataclass` 呢！？

## TL;DR

我们建议在新代码中使用现代 API：

- {func}`attrs.define` 用于定义新类，
- [`attrs.mutable()`](attrs.mutable) 是 {func}`attrs.define` 的别名，
- [`attrs.frozen()`](attrs.frozen) 是 `define(frozen=True)` 的别名，
- 以及 {func}`attrs.field()` 用于定义属性。

它们是在 *attrs* 20.1.0 中新增的，表达性强，并且具有现代默认设置，如插槽和类型注解默认启用。
有时，它们被称为 *下一代* 或 *NG* API。
自 *attrs* 21.3.0 起，你也可以从 `attrs` 包命名空间导入它们。

传统的，或称为 *OG* API {func}`attr.s` / {func}`attr.ib`，它们的严肃别名 `attr.attrs` / `attr.attrib`，以及从未记录但流行的 `attr.dataclass` 彩蛋将永远保留。

*attrs* **绝不会**强制你使用类型注解。

## 简短的历史课(A Short History Lesson)

到现在为止，*attrs* 已经是一个老项目。
它的第一次发布是在 2015 年 4 月 -- 当时大多数 Python 代码还在 Python 2.7 上，Python 3.4 是第一个展现潜力的 Python 3 版本。
*attrs* 一直以来都是以 Python 3 为主，但 [类型注解](https://peps.python.org/pep-0484/) 直到 2015 年 9 月的 Python 3.5 才发布，并在几年内基本上被忽视。

那时，如果你不想实现所有的 {term}`双下划线方法 <dunder methods>`，创建一个带有属性的类最常见的方法就是继承 {obj}`collections.namedtuple`，或者使用许多黑客手段，通过属性查找来访问字典键。

但 *attrs* 的历史可以追溯得更远，最早可以追溯到现在被遗忘的 [*characteristic*](https://github.com/hynek/characteristic)，它于 2014 年 5 月发布，已经使用了类装饰器，但整体上使用起来过于繁琐。

在这一背景下，[Glyph](https://github.com/glyph) 和 [Hynek](https://github.com/hynek) 在 IRC 上聚会，集思广益，想如何保留 *characteristic* 的好点子，但让它更易于使用和阅读。
当时的计划并不是将 *attrs* 打造成如今这样一个灵活的类构建工具。
我们只想要一个简洁的库来定义带有属性的类。

受困于笨拙的 `characteristic` 名称，我们决定从另一侧入手，使包名成为 API 的一部分，并保持 API 函数非常简短。
这导致了臭名昭著的 {func}`attr.s` 和 {func}`attr.ib`，一些人觉得这很困惑，并将其读作 “attr dot s” 或者使用单一的 `@s` 作为装饰器。
但这实际上只是表达 `attrs` 和 `attrib` 的一种方式[^attr]。

[^attr]: 我们也考虑过将 PyPI 包命名为 `attr`，但这个名称已经被一个 *表面上* 不活跃的 [包在 PyPI](https://pypi.org/project/attr/#history) 占用了。

一些人从一开始就讨厌这个可爱的 API，这就是我们添加别名的原因，称之为 *serious business*：`@attr.attrs` 和 `attr.attrib()`。
他们的粉丝通常只导入这些名称，而根本不使用包名。
不幸的是，`attr` 包名称在我们添加 `attr.Factory` 的那一刻开始显得不合适，因为它无法以任何方式被变成有意义的东西。
随着更多 API 和模块的添加，这个问题变得越来越严重。

但总体来说，*attrs* 以这种形式取得了 **巨大的** 成功 -- 特别是在 Glyph 的博客文章 [*The One Python Library Everyone Needs*](https://glyph.twistedmatrix.com/2016/08/attrs.html) 在 2016 年 8 月发布后，以及 [*pytest*](https://docs.pytest.org/) 采纳它之后。

能够简单地写：

```
@attr.s
class Point:
    x = attr.ib()
    y = attr.ib()
```

对于那些想要编写小而专注的类的人来说，这是一个重要的进步。

### Dataclasses 加入的竞争(Dataclasses Enter The Arena)

2017 年 5 月发生了一次重大变化，当时 Hynek 和 [Guido van Rossum](https://en.wikipedia.org/wiki/Guido_van_Rossum) 以及 [Eric V. Smith](https://github.com/ericvsmith) 在 PyCon US 2017 上坐在一起。

类属性的类型注解刚刚在 Python 3.6 中到来，Guido 觉得引入类似于 *attrs* 的机制到 Python 标准库中是个好主意。
结果当然是 {pep}`557`[^stdlib]，这最终成为了 Python 3.7 中的 `dataclasses` 模块。

[^stdlib]: 这篇高度可读的 PEP 还解释了为什么 *attrs* 并没有被直接添加到标准库中。
    不要相信那些神话和谣言。

在这一点上，*attrs* 很幸运，有几个人也对类型注解非常感兴趣，并帮助实现它；包括一个 [Mypy 插件](https://medium.com/@Pilot-EPD-Blog/mypy-and-attrs-e1b0225e9ac6)。
于是 *attrs* 在 Python 3.7 发布之前的半年多时间里 [发布](https://www.attrs.org/en/17.3.0.post2/changelog.html) 了新的类定义方法，因此 `dataclasses` 也随之问世。

---

由于向后兼容性的考虑，这个特性在 {func}`attr.s` 装饰器中默认是关闭的，必须使用 `@attr.s(auto_attribs=True)` 来激活。
作为一个小彩蛋，为了节省打字，我们还 [添加](https://github.com/python-attrs/attrs/commit/88aa1c897dfe2ee4aa987e4a56f2ba1344a17238#diff-4fc63db1f2fcb7c6e464ee9a77c3c74e90dd191d1c9ffc3bdd1234d3a6663dc0R48) 了一个别名 `attr.dataclass`，它只是设置了 `auto_attribs=True`。
这个别名从未被记录，但人们发现并使用它，并对此非常喜爱。

在接下来的几个月和几年中，显然类型注解已经成为定义类及其属性的流行方式。
然而，也有一些人对类型注解表现出强烈的厌恶。
我们决心服务于双方。

### *attrs* TNG

在其存在期间，*attrs* 从未停滞不前。
但是由于我们非常重视向后兼容性，并不希望破坏用户的代码，许多功能和优点必须手动激活。

这不仅令人恼火，而且还导致许多 *attrs* 的用户甚至不知道它能为他们做什么。
我们花了多年的时间在解释，使用类型注解定义属性绝对不是 {mod}`dataclasses` 独有的。

最终，我们决定采取 [Go 的做法](https://go.dev/blog/module-compatibility)：
与其处理那些感觉过时的旧 API，我们不如定义新的 API，并提供更好的默认值。
因此在 2018 年 7 月，我们 [寻找更好的名称](https://github.com/python-attrs/attrs/issues/408)，想出了 {func}`attr.define`、{func}`attr.field` 等等。
然后在 2019 年 1 月，我们 [开始寻找不便的默认值](https://github.com/python-attrs/attrs/issues/487)，现在我们可以在没有任何后果的情况下进行修复。

这些新 API 证明非常受欢迎，因此我们终于在 2021 年 11 月将文档改为使用这些 API。

当然，这一切花了太长时间。
一个原因是 COVID-19 大流行，但还有我们的担忧，不希望在这一历史性机会中搞砸我们的 API。

最终，在 2021 年 12 月，我们添加了 *attrs* 包命名空间。

我们希望你喜欢这个结果：

```
from attrs import define

@define
class Point:
    x: int
    y: int
```
