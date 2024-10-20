# *attrs*: Classes Without Boilerplate

Release **{sub-ref}`release`**  ([What's new?](changelog.md))

```{include} ../README.md
:start-after: 'teaser-begin -->'
:end-before: '<!-- sponsor-break-begin'
```

<!-- [[[cog
# This is mainly called from RTD's pre_build job!

import pathlib, tomllib

for sponsor in tomllib.loads(pathlib.Path("pyproject.toml").read_text())["tool"]["sponcon"]["sponsors"]:
      print(f'<a href="{sponsor["url"]}"><img title="{sponsor["title"]}" src="_static/sponsors/{sponsor["img"]}" width="190" /></a>')
]]] -->
<a href="https://www.variomedia.de/"><img title="Variomedia AG" src="_static/sponsors/Variomedia.svg" width="190" /></a>
<a href="https://tidelift.com/?utm_source=lifter&utm_medium=referral&utm_campaign=hynek"><img title="Tidelift" src="_static/sponsors/Tidelift.svg" width="190" /></a>
<a href="https://klaviyo.com/"><img title="Klaviyo" src="_static/sponsors/Klaviyo.svg" width="190" /></a>
<a href="https://filepreviews.io/"><img title="FilePreviews" src="_static/sponsors/FilePreviews.svg" width="190" /></a>
<a href="https://polar.sh/"><img title="Polar" src="_static/sponsors/Polar.svg" width="190" /></a>
<!-- [[[end]]] -->

```{include} ../README.md
:start-after: 'sponsor-break-end -->'
:end-before: '<!-- teaser-end'
```


## 入门指南

*attrs* 是一个仅适用于 Python 的包，[托管在 PyPI](https://pypi.org/project/attrs/) 上。

以下步骤将帮助你快速上手：

- {doc}`overview` 将展示一个简单的 *attrs* 示例，并介绍它的设计理念。之后，你可以开始编写自己的类，理解 *attrs* 的设计驱动。
- {doc}`examples` 将带你全面了解 *attrs* 的功能。阅读后，你将掌握高级功能并知道如何使用它们。
- {doc}`why` 会介绍一些可能的替代方案，以及为什么我们认为 *attrs* 仍然值得使用——甚至在某些情况下，依你的需求可能是更好的选择。
- 如果你在任何时候对某些术语感到困惑，请查阅我们的 {doc}`glossary`。

如果在入门时需要帮助，欢迎在 [Stack Overflow](https://stackoverflow.com/questions/tagged/python-attrs) 上使用 `python-attrs` 标签寻求帮助，定会有人为你解答！

## 日常使用

- {doc}`types` 帮助你编写*正确*且*自文档化*的代码。*attrs* 对类型提供了一流的支持，但如果你不需要，也可以完全不使用它们！
- 实例初始化是 *attrs* 的关键功能之一。我们的目标是尽可能减少你需要编写的代码。{doc}`init` 提供了 *attrs* 所能提供的功能概述，并解释了我们所信奉的一些相关理念。
- 比较和排序对象是常见任务。{doc}`comparison` 展示了 *attrs* 如何帮助你实现这些任务，以及如何对其进行自定义。
- 如果你想将对象放入集合或作为字典的键，它们必须是可哈希的。最简单的方法是使用冻结类，但这个话题比看起来要复杂得多，{doc}`hashing` 会为你提供一些基本提示，让你知道需要注意什么。
- 一旦你熟悉了这些概念，我们的 {doc}`api` 包含了使用 *attrs* 的全部信息，帮助你充分利用它。
- *attrs* 从设计之初就为了扩展性而构建。{doc}`extending` 将向你展示它的扩展功能，以及如何将它作为你自己项目的构建模块。
- 最后，如果你对 `attr.s`、`attr.ib`、`attrs`、`attrib`、`define`、`frozen` 和 `field` 感到困惑，请前往 {doc}`names` 进行简短的解释，或者选择性地了解一下它们的历史。


## 面向企业的 *attrs*

```{include} ../README.md
:start-after: '### 面向企业的 *attrs*'
```

---

## 完整目录

```{toctree}
:maxdepth: 2
:caption: 入门

overview
why
examples
```

```{toctree}
:maxdepth: 2
:caption: 解释说明

types
init
comparison
hashing
```

```{toctree}
:maxdepth: 2
:caption: 参考

api
api-attr
glossary
```
```{toctree}
:maxdepth: 2
:caption: 高级用法

extending
how-does-it-work
```

```{toctree}
:caption: Meta
:maxdepth: 1

names
license
changelog
PyPI <https://pypi.org/project/attrs/>
GitHub <https://github.com/python-attrs/attrs>
第三方扩展 <https://github.com/python-attrs/attrs/wiki/Extensions-to-attrs>
贡献 <https://github.com/python-attrs/attrs/blob/main/.github/CONTRIBUTING.md>
基金 <https://hynek.me/say-thanks/>
```

[Full Index](genindex)
