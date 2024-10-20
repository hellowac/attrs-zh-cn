# 扩展(Extending)

每个 *attrs* 装饰的类都有一个 `__attrs_attrs__` 类属性。
它是一个包含关于每个属性元数据的 {class}`attrs.Attribute` 元组。

因此，构建自己的装饰器在 *attrs* 之上相当简单：

```{doctest}
>>> from attrs import define
>>> def print_attrs(cls):
...     print(cls.__attrs_attrs__)
...     return cls
>>> @print_attrs
... @define
... class C:
...     a: int
(Attribute(name='a', default=NOTHING, validator=None, repr=True, eq=True, eq_key=None, order=True, order_key=None, hash=None, init=True, metadata=mappingproxy({}), type=<class 'int'>, converter=None, kw_only=False, inherited=False, on_setattr=None, alias='a'),)
```

:::{warning}
{func}`attrs.define` / {func}`attr.s` 装饰器 **必须** 首先应用，因为它会放置 `__attrs_attrs__`！
这意味着它必须在你的装饰器 *之后*，因为：

```python
@a
@b
def f():
   pass
```

仅仅是 [语法糖](https://en.wikipedia.org/wiki/Syntactic_sugar) 的表现形式：

```python
def original_f():
   pass

f = a(b(original_f))
```
:::


## Wrapping装饰器(Wrapping the Decorator)

一种更优雅的方式是完全包装 *attrs* 并在其上构建一个类 [DSL](https://en.wikipedia.org/wiki/Domain-specific_language)。

一个例子是包 [*environ-config*](https://github.com/hynek/environ-config)，它在底层使用 *attrs* 以声明方式定义基于环境的配置，而不暴露 *attrs* API。

另一个常见用例是覆盖 *attrs* 的默认值。


### Mypy

不幸的是，装饰器包装目前会 [困扰](https://github.com/python/mypy/issues/5406) Mypy 的 *attrs* 插件。
此时，最佳的解决方法是忍耐一下，编写一个伪 Mypy 插件，并变更一堆全局变量：

```python
from mypy.plugin import Plugin
from mypy.plugins.attrs import (
   attr_attrib_makers,
   attr_class_makers,
   attr_dataclass_makers,
)

# 这些工作方式与 `attr.dataclass` 完全相同。
attr_dataclass_makers.add("my_module.method_looks_like_attr_dataclass")

# 这与 `attr.s` 的工作方式相同。
attr_class_makers.add("my_module.method_looks_like_attr_s")

# 这些是我们的 `attr.ib` 制作器。
attr_attrib_makers.add("my_module.method_looks_like_attrib")

class MyPlugin(Plugin):
    # 我们的插件什么都不做，但它必须存在，以便这个文件被加载。
    pass


def plugin(version):
    return MyPlugin
```

然后使用项目的 `mypy.ini` 告诉 Mypy 关于你的插件：

```ini
[mypy]
plugins=<path to file>
```

:::{warning}
请注意，目前 *不可能* 让 Mypy 知道你已经更改了默认值，例如 *eq* 或 *order*。
你只能使用这个技巧告诉 Mypy 一个类实际上是一个 *attrs* 类。
:::


### Pyright

通用装饰器包装在 [Pyright](https://github.com/microsoft/pyright) 中通过 `typing.dataclass_transform` / {pep}`681` 得到了支持。

对于自定义包装的形式：

```
@typing.dataclass_transform(field_specifiers=(attr.attrib, attrs.field))
def custom_define(f):
    return attrs.define(f)
```

## 类型(Types)

*attrs* 提供了两种将类型信息附加到属性的方法：

- {pep}`526` 注解，
- 以及传递给 {func}`attr.ib` / {func}`attrs.field` 的 *type* 参数。

这些信息对你来说是可用的：

```{doctest}
>>> from attrs import define, field, fields
>>> @define
... class C:
...     x: int = field()
...     y = field(type=str)
>>> fields(C).x.type
<class 'int'>
>>> fields(C).y.type
<class 'str'>
```

目前，*attrs* 并不对这些信息做任何处理，但如果你想编写自己的验证器或序列化器，这非常有用！

最初，我们没有将 *type* 参数添加到新的 {func}`attrs.field` API，因为类型注解是首选方式。
但我们后来重新引入了它，以便 `field` 可以与 {func}`attrs.make_class` 函数一起使用。
我们强烈不建议在 {func}`attrs.make_class` 之外使用 *type* 参数。

(extending-metadata)=

## 元数据(Metadata)

如果你是一个与 *attrs* 集成的第三方库的作者，你可能想要利用属性元数据。

以下是有效使用元数据的一些提示：

- 尝试使你的元数据键和值不可变。
  这也会保持整个 {class}`~attrs.Attribute` 实例不可变。

- 为了避免元数据键冲突，考虑从你的模块中公开你的元数据键：

  ```python
  from mylib import MY_METADATA_KEY

  @define
  class C:
    x = field(metadata={MY_METADATA_KEY: 1})
  ```

  元数据应该是可组合的，因此即使你决定以以下方式之一实现你的元数据，也要考虑支持这种方法。

- 为你的特定元数据公开 `field` 包装器。
  如果你的用户不需要来自其他库的元数据，这是更优雅的方法。

  ```{doctest}
  >>> from attrs import fields, NOTHING
  >>> MY_TYPE_METADATA = '__my_type_metadata'
  >>>
  >>> def typed(
  ...     cls, default=NOTHING, validator=None, repr=True,
  ...     eq=True, order=None, hash=None, init=True, metadata=None,
  ...     converter=None
  ... ):
  ...     metadata = metadata or {}
  ...     metadata[MY_TYPE_METADATA] = cls
  ...     return field(
  ...         default=default, validator=validator, repr=repr,
  ...         eq=eq, order=order, hash=hash, init=init,
  ...         metadata=metadata, converter=converter
  ...     )
  >>>
  >>> @define
  ... class C:
  ...     x: int = typed(int, default=1, init=False)
  >>> fields(C).x.metadata[MY_TYPE_METADATA]
  <class 'int'>
  ```

(transform-fields)=

## 自动生成字段的转换和修改(Automatic Field Transformation and Modification)

*attrs* 允许你在类创建时自动修改或转换类的字段。
你可以通过将 *field_transformer* 钩子传递给 {func}`~attrs.define`（及其相关函数）来实现这一点。
其主要目的是基于字段类型自动添加转换器，以帮助 API 客户端和其他类型化数据加载器的开发。

此钩子必须具有以下签名：

```{eval-rst}
.. function:: your_hook(cls: type, fields: list[attrs.Attribute]) -> list[attrs.Attribute]
   :noindex:
```

- *cls* 是在转换为 attrs 类之前的类。
  这意味着它尚未拥有 `__attrs_attrs__` 属性。
- *fields* 是将来将设置为 `__attrs_attrs__` 的所有 `attrs.Attribute` 实例的列表。
  你可以以任何方式修改这些属性：
  你可以添加转换器、改变类型，甚至完全删除属性或创建新的属性！

例如，假设你真的不喜欢浮点数：

```{doctest}
>>> def drop_floats(cls, fields):
...     return [f for f in fields if f.type not in {float, 'float'}]
...
>>> @frozen(field_transformer=drop_floats)
... class Data:
...     a: int
...     b: float
...     c: str
...
>>> Data(42, "spam")
Data(a=42, c='spam')
```

一个更现实的例子是自动转换你从 JSON 加载的数据：

```{doctest}
>>> from datetime import datetime
>>>
>>> def auto_convert(cls, fields):
...     results = []
...     for field in fields:
...         if field.converter is not None:
...             results.append(field)
...             continue
...         if field.type in {datetime, 'datetime'}:
...             converter = (lambda d: datetime.fromisoformat(d) if isinstance(d, str) else d)
...         else:
...             converter = None
...         results.append(field.evolve(converter=converter))
...     return results
...
>>> @frozen(field_transformer=auto_convert)
... class Data:
...     a: int
...     b: str
...     c: datetime
...
>>> from_json = {"a": 3, "b": "spam", "c": "2020-05-04T13:37:00"}
>>> Data(**from_json)  # ****
Data(a=3, b='spam', c=datetime.datetime(2020, 5, 4, 13, 37))
```

或者，你可能更愿意通过默认字段 *别名* 生成与数据类兼容的 `__init__` 签名。
请注意，*field_transformer* 在应用默认私有属性处理之前对 {class}`attrs.Attribute` 实例进行操作，因此可以检测到显式用户提供的别名。

```{doctest}
>>> def dataclass_names(cls, fields):
...     return [
...         field.evolve(alias=field.name)
...         if not field.alias
...         else field
...         for field in fields
...     ]
...
>>> @frozen(field_transformer=dataclass_names)
... class Data:
...     public: int
...     _private: str
...     explicit: str = field(alias="aliased_name")
...
>>> Data(public=42, _private="spam", aliased_name="yes")
Data(public=42, _private='spam', explicit='yes')
```

## 在 `asdict()` 中自定义字段的序列化(Customize Value Serialization in `asdict()`)

*attrs* 允许你使用 {func}`attrs.asdict` 函数将 *attrs* 类的实例序列化为字典。
然而，结果并不总是可以序列化，因为大多数数据类型将保持原样：

```{doctest}
>>> import json
>>> import datetime
>>> from attrs import asdict
>>>
>>> @frozen
... class Data:
...    dt: datetime.datetime
...
>>> data = asdict(Data(datetime.datetime(2020, 5, 4, 13, 37)))
>>> data
{'dt': datetime.datetime(2020, 5, 4, 13, 37)}
>>> json.dumps(data)
Traceback (most recent call last):
   ...
TypeError: Object of type datetime is not JSON serializable
```

为了解决这个问题，{func}`~attrs.asdict` 允许你传递一个 *value_serializer* 钩子。
它的签名为：

```{eval-rst}
.. function:: your_hook(inst: type, field: attrs.Attribute, value: typing.Any) -> typing.Any
   :noindex:
```

```{doctest}
>>> from attr import asdict
>>> def serialize(inst, field, value):
...     if isinstance(value, datetime.datetime):
...         return value.isoformat()
...     return value
...
>>> data = asdict(
...     Data(datetime.datetime(2020, 5, 4, 13, 37)),
...     value_serializer=serialize,
... )
>>> data
{'dt': '2020-05-04T13:37:00'}
>>> json.dumps(data)
'{"dt": "2020-05-04T13:37:00"}'
```
