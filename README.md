<p align="center">
   <a href="https://www.attrs.org/">
      <picture>
         <source srcset="https://raw.githubusercontent.com/python-attrs/attrs/main/docs/_static/attrs_logo_white.svg" media="(prefers-color-scheme: dark)">
         <img src="https://raw.githubusercontent.com/python-attrs/attrs/main/docs/_static/attrs_logo.svg" width="35%" alt="attrs" />
      </picture>
   </a>
</p>

<p align="center">
   <a href="https://www.attrs.org/en/stable/"><img src="https://img.shields.io/badge/Docs-RTD-black" alt="Documentation" /></a>
   <a href="https://github.com/python-attrs/attrs/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-C06524" alt="License: MIT" /></a>
   <a href="https://bestpractices.coreinfrastructure.org/projects/6482"><img src="https://bestpractices.coreinfrastructure.org/projects/6482/badge"></a>
   <a href="https://pypi.org/project/attrs/"><img src="https://img.shields.io/pypi/v/attrs" /></a>
   <a href="https://pepy.tech/project/attrs"><img src="https://static.pepy.tech/personalized-badge/attrs?period=month&units=international_system&left_color=grey&right_color=blue&left_text=Downloads%20/%20Month" alt="Downloads per month" /></a>
   <a href="https://zenodo.org/badge/latestdoi/29918975"><img src="https://zenodo.org/badge/29918975.svg" alt="DOI"></a>
</p>

<!-- teaser-begin -->

*attrs* 是一个 Python 包，它将通过免除你实现对象协议（即 [双下方法](https://www.attrs.org/en/latest/glossary.html#term-dunder-methods)）的繁琐工作，重新带回**编写类**的**乐趣**。自 2020 年以来，它已被 [NASA 信赖](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/personalizing-your-profile#list-of-qualifying-repositories-for-mars-2020-helicopter-contributor-achievement) 并用于火星任务！

它的主要目标是帮助你编写**简洁**且**正确**的软件，同时不降低代码的执行效率。


## 赞助商

*attrs* 项目离不开我们 [优秀的赞助商](https://github.com/sponsors/hynek) 的支持。
特别是那些慷慨支持我们 *The Organization* 级别及更高级别的赞助商：

<!-- sponsor-break-begin -->

<p align="center">

<!-- [[[cog
import pathlib, tomllib

for sponsor in tomllib.loads(pathlib.Path("pyproject.toml").read_text())["tool"]["sponcon"]["sponsors"]:
      print(f'<a href="{sponsor["url"]}"><img title="{sponsor["title"]}" src="docs/_static/sponsors/{sponsor["img"]}" width="190" /></a>')
]]] -->
<a href="https://www.variomedia.de/"><img title="Variomedia AG" src="docs/_static/sponsors/Variomedia.svg" width="190" /></a>
<a href="https://tidelift.com/?utm_source=lifter&utm_medium=referral&utm_campaign=hynek"><img title="Tidelift" src="docs/_static/sponsors/Tidelift.svg" width="190" /></a>
<a href="https://klaviyo.com/"><img title="Klaviyo" src="docs/_static/sponsors/Klaviyo.svg" width="190" /></a>
<a href="https://filepreviews.io/"><img title="FilePreviews" src="docs/_static/sponsors/FilePreviews.svg" width="190" /></a>
<a href="https://polar.sh/"><img title="Polar" src="docs/_static/sponsors/Polar.svg" width="190" /></a>
<!-- [[[end]]] -->

</p>

<!-- sponsor-break-end -->

<p align="center">
   <strong>请考虑<a href="https://github.com/sponsors/hynek">加入他们</a>，帮助使 <em>attrs</em> 的维护更加可持续！</strong>
</p>

<!-- teaser-end -->

## 示例

*attrs* 提供了一个类装饰器，以及一种声明式定义类属性的方式：

<!-- code-begin -->

```pycon
>>> from attrs import asdict, define, make_class, Factory

>>> @define
... class SomeClass:
...     a_number: int = 42
...     list_of_numbers: list[int] = Factory(list)
...
...     def hard_math(self, another_number):
...         return self.a_number + sum(self.list_of_numbers) * another_number


>>> sc = SomeClass(1, [1, 2, 3])
>>> sc
SomeClass(a_number=1, list_of_numbers=[1, 2, 3])

>>> sc.hard_math(3)
19
>>> sc == SomeClass(1, [1, 2, 3])
True
>>> sc != SomeClass(2, [3, 2, 1])
True

>>> asdict(sc)
{'a_number': 1, 'list_of_numbers': [1, 2, 3]}

>>> SomeClass()
SomeClass(a_number=42, list_of_numbers=[])

>>> C = make_class("C", ["a", "b"])
>>> C("foo", "bar")
C(a='foo', b='bar')
```

在*声明*了属性之后，*attrs* 为你提供：

- 简洁明了的类属性概览，
- 人类可读的 `__repr__`，
- 等值检查方法，
- 初始化器，
- 以及更多功能，

**不需要**重复编写无聊的样板代码，并且**不会**带来运行时性能的损失。

---

这个例子使用了 *attrs* 现代 API，它在 20.1.0 版本中引入，而 *attrs* 包的导入名称则在 21.3.0 版本中加入。
经典 API（如 `@attr.s`、`attr.ib` 以及它们的正式别名）和 `attr` 包的导入名称将**无限期**保留。

查看 [*关于核心 API 名称*](https://www.attrs.org/en/latest/names.html) 了解详细解释！


### 讨厌类型注解！？

没问题！
在 *attrs* 中，类型是完全**可选**的。
你可以简单地将 `attrs.field()` 赋值给属性，而不是使用类型注解：

```python
from attrs import define, field

@define
class SomeClass:
    a_number = field(default=42)
    list_of_numbers = field(factory=list)
```

## 数据类

乍一看，*attrs* 可能让你联想到 `dataclasses`（事实上，`dataclasses` [确实是 *attrs* 的后代](https://hynek.me/articles/import-attrs/)）。
但在实际应用中，*attrs* 提供了更多的功能，并且更灵活。
例如，它允许你定义[NumPy 数组的特殊处理，以进行相等性检查](https://www.attrs.org/en/stable/comparison.html#customization)，提供了更多的方式来[接入初始化过程](https://www.attrs.org/en/stable/init.html#hooking-yourself-into-initialization)，并提供了 `__init_subclass__` 的替代方法，甚至允许你通过调试器逐步执行生成的方法。

想了解更多细节，请查看我们的[对比页面](https://www.attrs.org/en/stable/why.html#data-classes)，但一般来说，我们更有可能为了实现某些预期的功能而“打破常规”，尽管这些功能在实际操作中可能非常复杂。

## 项目信息

- [**更新日志**](https://www.attrs.org/en/stable/changelog.html)
- [**文档**](https://www.attrs.org/)
- [**PyPI**](https://pypi.org/project/attrs/)
- [**源代码**](https://github.com/python-attrs/attrs)
- [**贡献指南**](https://github.com/python-attrs/attrs/blob/main/.github/CONTRIBUTING.md)
- [**第三方扩展**](https://github.com/python-attrs/attrs/wiki/Extensions-to-attrs)
- **寻求帮助**：在 [Stack Overflow](https://stackoverflow.com/questions/tagged/python-attrs) 上使用 `python-attrs` 标签

### 面向企业的 *attrs*

可作为 [Tidelift 订阅服务](https://tidelift.com/?utm_source=lifter&utm_medium=referral&utm_campaign=hynek) 的一部分提供。

*attrs* 的维护者与数千个其他包的开发者正在与 Tidelift 合作，为你在构建应用程序时使用的开源包提供商业支持和维护。
节省时间，降低风险，改善代码健康，同时为你实际使用的包的维护者提供报酬。
