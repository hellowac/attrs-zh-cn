# 初始化(Initialization)

在 Python 中，实例初始化发生在 `__init__` 方法中。
一般来说，您应该尽量保持其逻辑简单，并应考虑类所需的内容，而不是如何实例化它。

将复杂对象传递给 `__init__` 并使用它们派生类的数据，不必要地将您的新类与旧类耦合，这使得测试变得更加困难，并且会导致后续问题。

因此，假设您使用 ORM 并想从行对象中提取 2D 点，请不要写这样的代码：

```python
class Point:
    def __init__(self, database_row):
        self.x = database_row.x
        self.y = database_row.y

pt = Point(row)
```

相反，请编写一个 {obj}`classmethod` 来提取它：

```python
@define
class Point:
    x: float
    y: float

    @classmethod
    def from_row(cls, row):
        return cls(row.x, row.y)

pt = Point.from_row(row)
```

这有时被称为 *命名构造函数* 或 *工厂方法*。

现在，您可以实例化 `Point`，而无需在测试中创建虚假的行对象。
您还可以有尽可能多的智能创建辅助函数。
这种灵活性非常有用，因为额外的数据源往往会随着时间而出现。

---

出于类似的原因，我们强烈不建议使用以下模式：

```python
pt = Point(**row.attributes)
```

这将您的类与数据库数据模型耦合。
尝试以干净且方便的方式设计类，而不是基于数据库格式。
数据库格式可以随时更改，而您却被迫使用难以更改的糟糕类设计。
将函数和类方法作为现实与您工作所需的最佳形式之间的过滤器。

:::{重要}
虽然 *attrs* 的初始化概念（包括后续关于验证器和转换器的部分）非常强大，但它们 **并不** 旨在替代功能齐全的序列化或验证系统。

我们希望帮助您编写一个您愿意手动编写的 `__init__`，但可以减少样板代码。

如果您在寻找强大而不具侵入性的序列化和验证功能以供您的 *attrs* 类使用，请查看我们的姐妹项目 [*cattrs*](https://catt.rs/) 或我们的 [第三方扩展](https://github.com/python-attrs/attrs/wiki/Extensions-to-attrs)。

这种创建类与序列化的分离是一个有意识的设计决策。
我们认为您的业务模型和序列化格式不应耦合。
:::

(private-attributes)=

## 私有属性和别名(Private Attributes and Aliases)

人们往往对以一个下划线开头的私有属性的处理感到困惑。
尽管存在 [一个约定](https://docs.python.org/3/tutorial/classes.html#tut-private)，即以下划线开头的对象成员应该被视为私有，但考虑到 *attrs* 的一个核心特性是自动创建一个 `__init__` 方法，其参数对应于成员。
对于私有参数没有相应的约定：函数的整个签名是其供调用者使用的公共接口。

然而，有时在构造对象时接受一个公共参数是有用的，但在对象创建后将该属性视为私有，可能是为了维护某些不变性。
作为该用例的便利，*attrs* 的默认行为是，如果您指定一个以下划线开头的成员，它将在创建 `__init__` 方法签名时去掉下划线：

```{doctest}
>>> import inspect
>>> from attrs import define
>>> @define
... class FileDescriptor:
...    _fd: int
>>> inspect.signature(FileDescriptor.__init__)
<Signature (self, fd: int) -> None>
```

即使您不使用此功能，了解它也是很重要的，因为它可能导致意外的语法错误：

```{doctest}
>>> @define
... class C:
...    _1: int
Traceback (most recent call last):
   ...
SyntaxError: invalid syntax
```

在这种情况下，一个有效的属性名 `_1` 被转变为一个无效的参数名 `1`。

这个功能是否对您有用是个人口味的问题。
如果您的口味不同，可以使用 *alias* 参数来 {func}`attrs.field` 明确设置参数名。
这可以用于覆盖私有属性的处理，或对 `__init__` 参数名进行其他任意更改。

```{doctest}
>>> from attrs import field
>>> @define
... class C:
...    _x: int = field(alias="_x")
...    y: int = field(alias="distasteful_y")
...    _1: int = field(alias="underscore1")
>>> inspect.signature(C.__init__)
<Signature (self, _x: int, distasteful_y: int, underscore1: int) -> None>
```

(defaults)=

## 默认值(Defaults)

有时您不想将所有属性值传递给类。
有时，某些属性甚至不打算传递，但您希望允许自定义以便于测试。

这时默认值就派上用场了：

```{doctest}
>>> from attrs import Factory
>>> @define
... class C:
...     a: int = 42
...     b: list = field(factory=list)
...     c: list = Factory(list)  # 上面的语法糖
...     d: dict = field()
...     @d.default
...     def _any_name_except_a_name_of_an_attribute(self):
...        return {}
>>> C()
C(a=42, b=[], c=[], d={})
```

重要的是，被装饰的方法（或任何其他方法或属性！）不能与属性同名，否则将覆盖属性定义。

类似于[常见的可变默认参数问题](https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments)，`default=[]`将*不会*执行您可能认为的那样：

```{doctest}
>>> @define
... class C:
...     x = []
>>> i = C()
>>> k = C()
>>> i.x.append(42)
>>> k.x
[42]
```

这就是*attrs* 提供工厂选项的原因。

:::{warning}
请注意，基于装饰器的默认值有一个陷阱：
它们在属性被设置时执行，这意味着根据属性的顺序，在调用时，`self` 对象可能尚未完全初始化。

因此，您应该尽量少使用 `self`。

即使是我们中最聪明的人也可能会[感到困惑](https://github.com/python-attrs/attrs/issues/289)，如果您传递的是部分初始化的对象，会发生什么。 
:::

(validators)=

## 验证器(Validators)

另一个绝对应该在 `__init__` 中完成的事情是检查结果实例是否符合不变性。这就是 *attrs* 引入验证器概念的原因。

### 装饰器(Decorator)

最简单的方法是使用属性的 `validator` 方法作为装饰器。

该方法必须接受三个参数：

1. 被验证的 *实例*（即 `self`），
2. 正在验证的 *属性*，以及最后
3. 传递给它的 *值*。

这些值作为 *位置参数* 传递，因此它们的名称无关紧要。

如果值未通过验证器的标准，它将引发适当的异常。

```{doctest}
>>> @define
... class C:
...     x: int = field()
...     @x.validator
...     def _check_x(self, attribute, value):
...         if value > 42:
...             raise ValueError("x must be smaller or equal to 42")
>>> C(42)
C(x=42)
>>> C(43)
Traceback (most recent call last):
   ...
ValueError: x must be smaller or equal to 42
```

同样，重要的是被装饰的方法不能与属性同名，并且必须使用 {func}`attrs.field` 辅助函数。


### 可调用对象(Callables)

如果你想重用你的验证器，你应该查看 {func}`attrs.field` 的 `validator` 参数。

它接受一个可调用对象或一个可调用对象列表（通常是函数），并将它们视为接收与装饰器方法相同参数的验证器。同样，与装饰器方法一样，它们作为 *位置参数* 传递，因此你可以随意命名它们。

由于验证器在实例初始化 *之后* 运行，你可以在验证时引用其他属性：

```{doctest}
>>> import attrs
>>> def x_smaller_than_y(instance, attribute, value):
...     if value >= instance.y:
...         raise ValueError("'x' has to be smaller than 'y'!")
>>> @define
... class C:
...     x = field(validator=[attrs.validators.instance_of(int),
...                          x_smaller_than_y])
...     y = field()
>>> C(x=3, y=4)
C(x=3, y=4)
>>> C(x=4, y=3)
Traceback (most recent call last):
   ...
ValueError: 'x' has to be smaller than 'y'!
```

这个示例演示了一种便利的快捷方式：
直接传递验证器列表等同于将它们包裹在 {obj}`attrs.validators.and_` 验证器中，并且所有验证器必须都通过。

*attrs* 不会拦截你对这些属性的更改，但你可以随时在任何实例上调用 {func}`attrs.validate` 来验证它是否仍然有效：

然而，当使用 {func}`attrs.define` 或 [`attrs.frozen`](attrs.frozen) 时，*attrs* 将在设置属性时运行验证器。

```{doctest}
>>> i = C(4, 5)
>>> i.x = 5
Traceback (most recent call last):
   ...
ValueError: 'x' has to be smaller than 'y'!
```

*attrs* 随附了一些验证器，请确保在编写自己的验证器之前 [查看它们]( api-validators)：

```{doctest}
>>> @define
... class C:
...     x = field(validator=attrs.validators.instance_of(int))
>>> C(42)
C(x=42)
>>> C("42")
Traceback (most recent call last):
   ...
TypeError: ("'x' must be <type 'int'> (got '42' that is a <type 'str'>).", Attribute(name='x', default=NOTHING, factory=NOTHING, validator=<instance_of validator for type <type 'int'>>, type=None), <type 'int'>, '42')
```

当然，你可以根据需要混合和匹配这两种方法。
如果你为一个属性使用两种方式定义验证器，它们都会被运行：

```{doctest}
>>> @define
... class C:
...     x = field(validator=attrs.validators.instance_of(int))
...     @x.validator
...     def fits_byte(self, attribute, value):
...         if not 0 <= value < 256:
...             raise ValueError("value out of bounds")
>>> C(128)
C(x=128)
>>> C("128")
Traceback (most recent call last):
   ...
TypeError: ("'x' must be <class 'int'> (got '128' that is a <class 'str'>).", Attribute(name='x', default=NOTHING, validator=[<instance_of validator for type <class 'int'>>, <function fits_byte at 0x10fd7a0d0>], repr=True, cmp=True, hash=True, init=True, metadata=mappingproxy({}), type=None, converter=None), <class 'int'>, '128')
>>> C(256)
Traceback (most recent call last):
   ...
ValueError: value out of bounds
```

最后，验证器可以被全局禁用：

```{doctest}
>>> attrs.validators.set_disabled(True)
>>> C("128")
C(x='128')
>>> attrs.validators.set_disabled(False)
>>> C("128")
Traceback (most recent call last):
   ...
TypeError: ("'x' must be <class 'int'> (got '128' that is a <class 'str'>).", Attribute(name='x', default=NOTHING, validator=[<instance_of validator for type <class 'int'>>, <function fits_byte at 0x10fd7a0d0>], repr=True, cmp=True, hash=True, init=True, metadata=mappingproxy({}), type=None, converter=None), <class 'int'>, '128')
```

... 或者在上下文管理器内：

```{doctest}
>>> with attrs.validators.disabled():
...     C("128")
C(x='128')
>>> C("128")
Traceback (most recent call last):
   ...
TypeError: ("'x' must be <class 'int'> (got '128' that is a <class 'str'>).", Attribute(name='x', default=NOTHING, validator=[<instance_of validator for type <class 'int'>>, <function fits_byte at 0x10fd7a0d0>], repr=True, cmp=True, hash=True, init=True, metadata=mappingproxy({}), type=None, converter=None), <class 'int'>, '128')
```

(converters)=

## 转换器(Converters)

有时，有必要规范化传入的值，因此 *attrs* 提供了转换器。

属性可以指定一个 `converter` 函数，该函数将在属性传入的值上被调用，以获取要使用的新值。这对于对值进行类型转换非常有用，而你不想强迫调用者去执行这些转换。

```{doctest}
>>> @define
... class C:
...     x = field(converter=int)
>>> o = C("1")
>>> o.x
1
>>> o.x = "2"
>>> o.x
2
```

转换器在 *验证器* 之前运行，因此你可以使用验证器来检查值的最终形式。

```{doctest}
>>> def validate_x(instance, attribute, value):
...     if value < 0:
...         raise ValueError("x must be at least 0.")
>>> @define
... class C:
...     x = field(converter=int, validator=validate_x)
>>> o = C("0")
>>> o.x
0
>>> C("-1")
Traceback (most recent call last):
   ...
ValueError: x must be at least 0.
```

可以说，你可以将转换器滥用为单参数验证器：

```{doctest}
>>> C("x")
Traceback (most recent call last):
   ...
ValueError: invalid literal for int() with base 10: 'x'
```

如果转换器的第一个参数有类型注解，则该类型将在 `__init__` 的签名中出现。转换器会覆盖显式的类型注解或 `type` 参数。

```{doctest}
>>> def str2int(x: str) -> int:
...     return int(x)
>>> @define
... class C:
...     x = field(converter=str2int)
>>> C.__init__.__annotations__
{'return': None, 'x': <class 'str'>}
```

如果你需要更多控制权来处理转换过程，可以用 {class}`attrs.Converter` 包装转换器，并要求提供正在初始化的实例和/或字段：

```{doctest}
>>> def complicated(value, self_, field):
...     return int(value) * self_.factor + field.metadata["offset"]
>>> @define
... class C:
...     factor = 5  # not an *attrs* field
...     x = field(
...         metadata={"offset": 200},
...         converter=attrs.Converter(
...             complicated,
...             takes_self=True, takes_field=True
...     ))
>>> C("42")
C(x=410)
```

## 将自己挂钩到初始化中(Hooking Yourself Into Initialization)

一般来说，当你意识到需要比 *attrs* 提供的更精细的控制来实例化类时，通常最好使用 {obj}`classmethod` 工厂或应用 [建造者模式](https://en.wikipedia.org/wiki/Builder_pattern)。

但是，有时你需要在类初始化之前或之后做某件快速的事情。为此，*attrs* 提供了以下选项：

- `__attrs_pre_init__` 会被自动检测并在 *attrs* 开始初始化之前运行。如果 `__attrs_pre_init__` 接受多个参数，*attrs* 生成的 `__init__` 将用它自身接收到的相同参数调用它。如果你需要注入对 `super().__init__()` 的调用（无论是否带参数），这非常有用。

- `__attrs_post_init__` 会被自动检测并在 *attrs* 完成实例初始化后运行。如果你想从其他属性中派生某个属性或对整个实例进行某种验证，这非常有用。

- `__attrs_init__` 是在 `__init__` 之 *前* 被写入并附加到你的类上的，如果 *attrs* 被告知不写一个（当 `init=False` 或通过 `auto_detect=True` 和自定义 `__init__` 的组合时）。如果你想完全控制初始化过程，但又不想手动设置属性，这非常有用。


### 预初始化(Pre Init)

`__attrs_pre_init__` 存在的唯一原因是给用户一个机会调用 `super().__init__()`，因为一些基于子类化的 API 需要这样做。

```{doctest}
>>> @define
... class C:
...     x: int
...     def __attrs_pre_init__(self):
...         super().__init__()
>>> C(42)
C(x=42)
```

如果你需要更多控制，可以使用下面描述的自定义初始化方法。

:::{warning}
你在继承其他 *attrs* 类的 *attrs* 类中永远不需要使用 `super()`。每个 *attrs* 类都会基于其自身的字段和所有基类的字段实现一个 `__init__`。

你只有在继承非 *attrs* 类时才需要这个逃生口。
:::

### 自定义初始化(Custom Init)

如果你告诉 *attrs* 不要写 `__init__`，它将改为写一个 `__attrs_init__`，代码与它将用于 `__init__` 的代码相同。你对初始化有完全的控制权，但也必须逐一输入参数的类型等。以下是手动默认值的示例：

```{doctest}
>>> @define
... class C:
...     x: int
...
...     def __init__(self, x: int = 42):
...         self.__attrs_init__(x)
>>> C()
C(x=42)
```

### 后初始化(Post Init)

```{doctest}
>>> @define
... class C:
...     x: int
...     y: int = field(init=False)
...     def __attrs_post_init__(self):
...         self.y = self.x + 1
>>> C(1)
C(x=1, y=2)
```

请注意，你无法在冻结类上直接设置属性：

```{doctest}
>>> @frozen
... class FrozenBroken:
...     x: int
...     y: int = field(init=False)
...     def __attrs_post_init__(self):
...         self.y = self.x + 1
>>> FrozenBroken(1)
Traceback (most recent call last):
   ...
attrs.exceptions.FrozenInstanceError: can't set attribute
```

如果你需要在冻结类上设置属性，你必须采用与 *attrs* 相同的 [技巧](how-frozen)，使用 {meth}`object.__setattr__`：

```{doctest}
>>> @define
... class Frozen:
...     x: int
...     y: int = field(init=False)
...     def __attrs_post_init__(self):
...         object.__setattr__(self, "y", self.x + 1)
>>> Frozen(1)
Frozen(x=1, y=2)
```

请注意，如果 `cache_hash=True`，你 *绝对不能* 在 `__attrs_post_init__` 中访问对象的哈希值。


## Order of Execution

如果存在，钩子的执行顺序如下：

1. `__attrs_pre_init__`（如果在 *当前* 类中存在）

2. 对于每个属性，按声明的顺序：

   1. 默认工厂
   2. 转换器

3. *所有* 验证器

4. `__attrs_post_init__`（如果在 *当前* 类中存在）

值得注意的是，这意味着你可以从验证器中访问所有属性，但转换器必须处理无效值，并且必须返回有效值。

## 派生属性(Derived Attributes)

在 *Stack Overflow* 上，关于 *attrs* 最常见的问题之一是如何使属性依赖于其他属性。
例如，如果你有一个 API 令牌，并希望实例化一个使用它进行身份验证的网络客户端。
基于前面的部分，有两种方法。

较简单的方法是使用 `__attrs_post_init__`：

```python
@define
class APIClient:
    token: str
    client: WebClient = field(init=False)

    def __attrs_post_init__(self):
        self.client = WebClient(self.token)
```

第二种方法是使用基于装饰器的默认值：

```python
@define
class APIClient:
    token: str
    client: WebClient = field()  # 必需！attr.ib 也可以

    @client.default
    def _client_factory(self):
        return WebClient(self.token)
```

话虽如此，正如本章开头指出的，更好的方法是使用工厂类方法：

```python
@define
class APIClient:
    client: WebClient

    @classmethod
    def from_token(cls, token: str) -> "APIClient":
        return cls(client=WebClient(token))
```

这使得类更具可测试性。

(init-subclass)=

## *attrs* 和 `__init_subclass__`

{meth}`object.__init_subclass__` 是一个特殊方法，当定义它的类的子类被创建时会被调用。

例如：

```{doctest}
>>> class Base:
...    @classmethod
...    def __init_subclass__(cls):
...        print(f"Base has been subclassed by {cls}.")
>>> class Derived(Base):
...    pass
Base has been subclassed by <class 'Derived'>.
```

不幸的是，像 *attrs*（或 `dataclasses`）这样的类装饰器方法与 `__init_subclass__` 的兼容性较差。
对于 {term}`字典类 <dict classes>`，该方法在类被 *attrs* 处理之前运行；而对于 {term}`插槽类 <slotted classes>`，由于 *attrs* 需要 *替换* 原始类，`__init_subclass__` 会被调用 *两次*：一次用于原始类，一次用于 *attrs* 类。

为了解决这个问题，*attrs* 提供了 `__attrs_init_subclass__`，它会在类组装完成后被调用。
基类甚至不必是 *attrs* 类：

```{doctest}
>>> class Base:
...    @classmethod
...    def __attrs_init_subclass__(cls):
...        print(f"Base has been subclassed by attrs {cls}.")
>>> @define
... class Derived(Base):
...    pass
Base has been subclassed by attrs <class 'Derived'>.
```
