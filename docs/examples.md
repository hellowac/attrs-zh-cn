# *attrs* 示例

## 基础(Basics)

最简单的用法是：

```{doctest}
>>> from attrs import define, field
>>> @define
... class Empty:
...     pass
>>> Empty()
Empty()
>>> Empty() == Empty()
True
>>> Empty() is Empty()
False
```

换句话说：即使没有实际的 {term}`fields <field>`，*attrs* 也有用！

不过，你通常会希望在类中添加一些数据，所以让我们加上一些：

```{doctest}
>>> @define
... class Coordinates:
...     x: int
...     y: int
```

默认情况下，所有特性都会被添加，因此你立即拥有一个功能齐全的数据类，包含一个简洁的 `repr` 字符串和比较方法。

```{doctest}
>>> c1 = Coordinates(1, 2)
>>> c1
Coordinates(x=1, y=2)
>>> c2 = Coordinates(x=2, y=1)
>>> c2
Coordinates(x=2, y=1)
>>> c1 == c2
False
```

如上所示，生成的 `__init__` 方法支持位置参数和关键字参数。

---

与 Data Classes 不同，*attrs* 不强制要求使用类型注解。因此，前面的例子也可以写成：

```{doctest}
>>> @define
... class Coordinates:
...     x = field()
...     y = field()
>>> Coordinates(1, 2)
Coordinates(x=1, y=2)
```

:::{caution}
如果类主体中包含一个使用 {func}`attrs.field`（或 {func}`attr.ib`）定义的字段，但**缺少类型注解**，*attrs* 将切换到无类型模式，并忽略那些具有类型注解但未使用 {func}`attrs.field`（或 {func}`attr.ib`）定义的字段。
:::

---

对于私有属性，*attrs* 会去掉关键字参数的前导下划线：

```{doctest}
>>> @define
... class C:
...     _x: int
>>> C(x=1)
C(_x=1)
```

如果你想自行初始化私有属性，也可以这样做：

```{doctest}
>>> @define
... class C:
...     _x: int = field(init=False, default=42)
>>> C()
C(_x=42)
>>> C(23)
Traceback (most recent call last):
   ...
TypeError: __init__() takes exactly 1 argument (2 given)
```

如果你更愿意公开私有属性，你可以使用关键字参数别名：

```{doctest}
>>> @define
... class C:
...     _x: int = field(alias="_x")
>>> C(_x=1)
C(_x=1)
```

还有另一种定义属性的方式，这在你想增强不是自己编写的类时非常有用（比如为 Django 模型增加一个简洁的 `__repr__` 方法）：

```{doctest}
>>> class SomethingFromSomeoneElse:
...     def __init__(self, x):
...         self.x = x
>>> SomethingFromSomeoneElse = define(
...     these={
...         "x": field()
...     }, init=False)(SomethingFromSomeoneElse)
>>> SomethingFromSomeoneElse(1)
SomethingFromSomeoneElse(x=1)
```

[继承对你不利](https://www.youtube.com/watch?v=3MNVP9-hglc)（除非进行[严格的专业化](https://hynek.me/articles/python-subclassing-redux/)），但 *attrs* 仍然会按照你期望的方式工作：

```{doctest}
>>> @define(slots=False)
... class A:
...     a: int
...     def get_a(self):
...         return self.a
>>> @define(slots=False)
... class B:
...     b: int
>>> @define(slots=False)
... class C(B, A):
...     c: int
>>> i = C(1, 2, 3)
>>> i
C(a=1, b=2, c=3)
>>> i == C(1, 2, 3)
True
>>> i.get_a()
1
```

{term}`Slotted classes <slotted classes>` 是新 API 的默认设置，它们与多重继承不兼容，因此我们在示例中没有使用。

属性的顺序由 [MRO](https://www.python.org/download/releases/2.3/mro/) 定义。


### 仅关键字属性(Keyword-only Attributes)

你还可以添加 [仅关键字](https://docs.python.org/3/glossary.html#keyword-only-parameter) 属性：

```{doctest}
>>> @define
... class A:
...     a: int = field(kw_only=True)
>>> A()
Traceback (most recent call last):
...
TypeError: A() missing 1 required keyword-only argument: 'a'
>>> A(a=1)
A(a=1)
```

`kw_only` 也可以在装饰器级别指定，并将应用于所有属性：

```{doctest}
>>> @define(kw_only=True)
... class A:
...     a: int
...     b: int
>>> A(1, 2)
Traceback (most recent call last):
...
TypeError: __init__() takes 1 positional argument but 3 were given
>>> A(a=1, b=2)
A(a=1, b=2)
```

如果你创建的属性使用 `init=False`，则 `kw_only` 参数会被忽略。

仅关键字属性允许子类添加没有默认值的属性，即使基类定义了带默认值的属性：

```{doctest}
>>> @define
... class A:
...     a: int = 0
>>> @define
... class B(A):
...     b: int = field(kw_only=True)
>>> B(b=1)
B(a=0, b=1)
>>> B()
Traceback (most recent call last):
...
TypeError: B() missing 1 required keyword-only argument: 'b'
```

如果你没有设置 `kw_only=True`，则没有有效的属性顺序，这会导致错误：

```{doctest}
>>> @define
... class A:
...     a: int = 0
>>> @define
... class B(A):
...     b: int
Traceback (most recent call last):
...
ValueError: No mandatory attributes allowed after an attribute with a default value or factory.  Attribute in question: Attribute(name='b', default=NOTHING, validator=None, repr=True, cmp=True, hash=None, init=True, converter=None, metadata=mappingproxy({}), type=int, kw_only=False)
```

(asdict)=

## 转换为集合类型(Converting to Collections Types)

当你有一个包含数据的类时，将该类转换为一个 {class}`dict` 通常非常方便（例如，如果你想将其序列化为 JSON）：

```{doctest}
>>> from attrs import asdict
>>> asdict(Coordinates(x=1, y=2))
{'x': 1, 'y': 2}
```

有些字段不能或不应该被转换。
为此，{func}`attrs.asdict` 提供了一个回调函数，用于决定一个属性是否应该被包含：

```{doctest}
>>> @define
... class User:
...     email: str
...     password: str

>>> @define
... class UserList:
...     users: list[User]

>>> asdict(UserList([User("jane@doe.invalid", "s33kred"),
...                  User("joe@doe.invalid", "p4ssw0rd")]),
...        filter=lambda attr, value: attr.name != "password")
{'users': [{'email': 'jane@doe.invalid'}, {'email': 'joe@doe.invalid'}]}
```

对于你想要 [`包含`](attrs.filters.include) 或 [`排除`](attrs.filters.exclude) 某些类型、字符串名称或属性的常见情况，*attrs* 提供了一些辅助函数：

```{doctest}
>>> from attrs import asdict, filters, fields

>>> @define
... class User:
...     login: str
...     password: str
...     email: str
...     id: int

>>> asdict(
...     User("jane", "s33kred", "jane@example.com", 42),
...     filter=filters.exclude(fields(User).password, "email", int))
{'login': 'jane'}

>>> @define
... class C:
...     x: str
...     y: str
...     z: int

>>> asdict(C("foo", "2", 3),
...        filter=filters.include(int, fields(C).x))
{'x': 'foo', 'z': 3}

>>> asdict(C("foo", "2", 3),
...        filter=filters.include(fields(C).x, "z"))
{'x': 'foo', 'z': 3}
```

:::{note}
虽然直接使用字符串名称很方便，但拼写错误的属性名称将静默地导致错误，并且无论是 Python 还是你的类型检查器都无法帮助你。
{func}`attrs.fields()` 会在字段不存在时引发 `AttributeError`，而字面字符串名称则不会。
在大多数情况下，使用 {func}`attrs.fields()` 来获取属性是值得推荐的。

```{doctest}
>>> asdict(
...     User("jane", "s33kred", "jane@example.com", 42),
...     filter=filters.exclude("passwd")
... )
{'login': 'jane', 'password': 's33kred', 'email': 'jane@example.com', 'id': 42}

>>> asdict(
...     User("jane", "s33kred", "jane@example.com", 42),
...     filter=fields(User).passwd
... )
Traceback (most recent call last):
...
AttributeError: 'UserAttributes' object has no attribute 'passwd'. Did you mean: 'password'?
```
:::

有时，你所需要的只是一个元组，而 *attrs* 不会让你失望：

```{doctest}
>>> import sqlite3
>>> from attrs import astuple

>>> @define
... class Foo:
...    a: int
...    b: int

>>> foo = Foo(2, 3)
>>> with sqlite3.connect(":memory:") as conn:
...    c = conn.cursor()
...    c.execute("CREATE TABLE foo (x INTEGER PRIMARY KEY ASC, y)") #doctest: +ELLIPSIS
...    c.execute("INSERT INTO foo VALUES (?, ?)", astuple(foo)) #doctest: +ELLIPSIS
...    foo2 = Foo(*c.execute("SELECT x, y FROM foo").fetchone())
<sqlite3.Cursor object at ...>
<sqlite3.Cursor object at ...>
>>> foo == foo2
True
```

对于更高级的转换和转化，我们建议你查看一个伴随库（例如 [*cattrs*](https://catt.rs/)）。


## 默认值(Defaults)

有时你希望为初始化函数提供默认值。
而有时你甚至希望可变对象作为默认值（你是否曾经不小心使用过 `def f(arg=[])`？）。
*attrs* 在这两种情况下都能满足你的需求：

```{doctest}
>>> import collections

>>> @define
... class Connection:
...     socket: int
...     @classmethod
...     def connect(cls, db_string):
...        # ... 以某种方式连接到 db_string ...
...        return cls(socket=42)

>>> @define
... class ConnectionPool:
...     db_string: str
...     pool: collections.deque = Factory(collections.deque)
...     debug: bool = False
...     def get_connection(self):
...         try:
...             return self.pool.pop()
...         except IndexError:
...             if self.debug:
...                 print("New connection!")
...             return Connection.connect(self.db_string)
...     def free_connection(self, conn):
...         if self.debug:
...             print("Connection returned!")
...         self.pool.appendleft(conn)
...
>>> cp = ConnectionPool("postgres://localhost")
>>> cp
ConnectionPool(db_string='postgres://localhost', pool=deque([]), debug=False)
>>> conn = cp.get_connection()
>>> conn
Connection(socket=42)
>>> cp.free_connection(conn)
>>> cp
ConnectionPool(db_string='postgres://localhost', pool=deque([Connection(socket=42)]), debug=False)
```

关于为什么用于构造对象的类方法很棒的更多信息，可以在这篇有见地的 [博客文章](https://web.archive.org/web/20210130220433/http://as.ynchrono.us/2014/12/asynchronous-object-initialization.html) 中找到。

默认工厂也可以通过 `factory` 参数设置为 {func}`~attrs.field`，并使用装饰器。
该方法接收部分初始化的实例，使你能够基于其他属性来设置默认值：

```{doctest}
>>> @define
... class C:
...     x: int = 1
...     y: int = field()
...     @y.default
...     def _any_name_except_a_name_of_an_attribute(self):
...         return self.x + 1
...     z: list = field(factory=list)
>>> C()
C(x=1, y=2, z=[])
```

请注意，装饰器方法 *仅* 在相关属性被赋值为 {func}`~attrs.field` 时有效。
因此，如果你使用 `@default`，单纯用类型注解并不足够。

(examples-validators)=

## 验证器(Validators)

尽管你的初始化函数应该尽量简洁（理想情况下：仅根据参数初始化实例！），但在参数上进行某种验证是很有用的。

*attrs* 提供了两种方法来为每个属性定义验证器，选择哪种方法更适合你的风格和项目就看你自己了。

你可以使用装饰器：

```{doctest}
>>> @define
... class C:
...     x: int = field()
...     @x.validator
...     def check(self, attribute, value):
...         if value > 42:
...             raise ValueError("x must be smaller or equal to 42")
>>> C(42)
C(x=42)
>>> C(43)
Traceback (most recent call last):
   ...
ValueError: x must be smaller or equal to 42
```

...或者使用可调用对象...

```{doctest}
>>> from attrs import validators

>>> def x_smaller_than_y(instance, attribute, value):
...     if value >= instance.y:
...         raise ValueError("'x' has to be smaller than 'y'!")
>>> @define
... class C:
...     x: int = field(validator=[validators.instance_of(int),
...                               x_smaller_than_y])
...     y: int
>>> C(x=3, y=4)
C(x=3, y=4)
>>> C(x=4, y=3)
Traceback (most recent call last):
   ...
ValueError: 'x' has to be smaller than 'y'!
```

...或者同时使用这两种方法：

```{doctest}
>>> @define
... class C:
...     x: int = field(validator=validators.instance_of(int))
...     @x.validator
...     def fits_byte(self, attribute, value):
...         if not 0 <= value < 256:
...             raise ValueError("value out of bounds")
>>> C(128)
C(x=128)
>>> C("128")
Traceback (most recent call last):
   ...
TypeError: ("'x' must be <class 'int'> (got '128' that is a <class 'str'>).", Attribute(name='x', default=NOTHING, validator=[<instance_of validator for type <class 'int'>>, <function fits_byte at 0x10fd7a0d0>], repr=True, cmp=True, hash=True, init=True, metadata=mappingproxy({}), type=int, converter=None, kw_only=False), <class 'int'>, '128')
>>> C(256)
Traceback (most recent call last):
   ...
ValueError: value out of bounds
```

请注意，装饰器方法仅在相关属性被赋值为 {func}`~attrs.field` 时有效。
因此，如果你使用 `@validator`，仅用类型注解并不足够。

*attrs* 附带了一些验证器，确保在编写自己的验证器之前先 [查看它们](api-validators)：

```{doctest}
>>> @define
... class C:
...     x: int = field(validator=validators.instance_of(int))
>>> C(42)
C(x=42)
>>> C("42")
Traceback (most recent call last):
   ...
TypeError: ("'x' must be <type 'int'> (got '42' that is a <type 'str'>).", Attribute(name='x', default=NOTHING, factory=NOTHING, validator=<instance_of validator for type <type 'int'>>, type=None, kw_only=False), <type 'int'>, '42')
```

如果使用旧式的 {func}`attr.s` 装饰器，验证器默认仅在初始化时运行。
如果使用较新的 {func}`attrs.define` 和其他相关方法，验证器在初始化时 *以及* 属性设置时都会运行。
这种行为可以通过 *on_setattr* 参数进行更改。

有关更多详细信息，请查看 {ref}`validators`。


## 转换(Conversion)

属性可以指定一个 `converter` 函数，该函数将被调用并传入属性的值，以获取要使用的新值。
这在对值进行类型转换时非常有用，因为你不想强迫调用者自己进行转换。

```{doctest}
>>> @define
... class C:
...     x: int = field(converter=int)
>>> o = C("1")
>>> o.x
1
>>> o.x = "2"
>>> o.x
2
```

如果使用旧式的 {func}`attr.s` 装饰器，转换器默认仅在初始化时运行。
如果使用较新的 {func}`attrs.define` 和其他相关方法，转换器在初始化时 *以及* 属性设置时都会运行。
这种行为可以通过 *on_setattr* 参数进行更改。

有关更多详细信息，请查看 {ref}`converters`。

(metadata)=

## 元数据(Metadata)

所有 *attrs* 属性都可以包含任意的元数据，形式为只读字典。

```{doctest}
>>> from attrs import fields

>>> @define
... class C:
...    x = field(metadata={'my_metadata': 1})
>>> fields(C).x.metadata
mappingproxy({'my_metadata': 1})
>>> fields(C).x.metadata['my_metadata']
1
```

元数据不被 *attrs* 使用，旨在为第三方库提供丰富的功能。
元数据字典遵循普通字典规则：
键需要是可哈希的，建议键和值都是不可变的。

如果您是具有 *attrs* 集成的第三方库的作者，请参阅 [*扩展元数据*](extending-metadata)。

## 类型(Types)

*attrs* 还允许您使用 *type* 参数或 {pep}`526` 注解或 {func}`attrs.field`/{func}`attr.ib` 来将类型与属性关联：

```{doctest}
>>> @define
... class C:
...     x: int
>>> fields(C).x.type
<class 'int'>

>>> import attr
>>> @attr.s
... class C:
...     x = attr.ib(type=int)
>>> fields(C).x.type
<class 'int'>
```

如果您不介意注解 *所有* 属性，您甚至可以省略 `attrs.field` 并分配默认值：

```{doctest}
>>> import typing

>>> @define
... class AutoC:
...     cls_var: typing.ClassVar[int] = 5  # 此项被忽略
...     l: list[int] = Factory(list)
...     x: int = 1
...     foo: str = "每个属性在 auto_attribs=True 时都需要一个类型"
...     bar: typing.Any = None
>>> fields(AutoC).l.type
list[int]
>>> fields(AutoC).x.type
<class 'int'>
>>> fields(AutoC).foo.type
<class 'str'>
>>> fields(AutoC).bar.type
typing.Any
>>> AutoC()
AutoC(l=[], x=1, foo='每个属性在 auto_attribs=True 时都需要一个类型', bar=None)
>>> AutoC.cls_var
5
```

生成的 `__init__` 方法将具有一个名为 `__annotations__` 的属性，该属性包含此类型信息。

如果您的注解包含字符串（例如，前向引用），
您可以通过使用 {func}`attrs.resolve_types` 在所有引用定义后解析这些字符串。
这将替换相应字段中的 *type* 属性。

```{doctest}
>>> from attrs import resolve_types

>>> @define
... class A:
...     a: 'list[A]'
...     b: 'B'
...
>>> @define
... class B:
...     a: A
...
>>> fields(A).a.type
'list[A]'
>>> fields(A).b.type
'B'
>>> resolve_types(A, globals(), locals())
<class 'A'>
>>> fields(A).a.type
list[A]
>>> fields(A).b.type
<class 'B'>
```

:::{note}
如果您发现自己使用字符串类型注解来处理前向引用，请将整个类型注解用引号包裹，而不仅仅是需要前向引用的类型（因此使用 `'list[A]'` 而不是 `list['A']`）。
这是 Python 类型系统的一个限制。
:::

:::{warning}
*attrs* 本身没有任何功能可以在类型元数据之上工作。
但是它对于编写自己的验证器或序列化框架很有用。
:::


## 槽(Slots)

{term}`槽类 <slotted classes>` 在 CPython 中有几个优势。
手动定义 `__slots__` 是繁琐的，而在 *attrs* 中，只需使用 {func}`attrs.define` 或传递 `slots=True` 给 {func}`attr.s`：

```{doctest}
>>> @define
... class Coordinates:
...     x: int
...     y: int

>>> import attr

>>> @attr.s(slots=True)
... class Coordinates:
...     x: int
...     y: int
```

{func}`~attrs.define` 默认设置 `slots=True`。

## 不可变性(Immutability)

有时候您会有一些在实例化后不应更改的实例。
不可变性在函数式编程中特别流行，通常是非常好的事情。
如果您想强制实现这一点，*attrs* 将尽力提供帮助：

```{doctest}
>>> from attrs import frozen

>>> @frozen
... class C:
...     x: int
>>> i = C(1)
>>> i.x = 2
Traceback (most recent call last):
   ...
attrs.exceptions.FrozenInstanceError: can't set attribute
>>> i.x
1
```

请注意，真正的不可变性在 Python 中是不可实现的，但它可以 [让你达到](how-frozen) 99% 的效果。
不可变类本身对于应该永远不变的长生命周期对象非常有用；例如配置。

为了在常规程序流程中使用它们，您需要一种轻松创建新实例以更改属性的方法。
在 Clojure 中，该函数称为 [*assoc*](https://clojuredocs.org/clojure.core/assoc)，而 *attrs* 毫不掩饰地模仿它：{func}`attrs.evolve`：

```{doctest}
>>> from attrs import evolve, frozen

>>> @frozen
... class C:
...     x: int
...     y: int
>>> i1 = C(1, 2)
>>> i1
C(x=1, y=2)
>>> i2 = evolve(i1, y=3)
>>> i2
C(x=1, y=3)
>>> i1 == i2
False
```

## 其他好东西

在构建具有类似插件接口的系统时，您可能希望有一个所有实现某个接口的类的注册表：

```{doctest}
>>> REGISTRY = []
>>> class Base:  # 不一定要是 attrs 类！
...     @classmethod
...     def __attrs_init_subclass__(cls):
...         REGISTRY.append(cls)
>>> @define
... class Impl(Base):
...     pass
>>> REGISTRY
[<class 'Impl'>]
```

有时您可能希望以编程方式创建一个类。
*attrs* 为此提供了 {func}`attrs.make_class`：

```{doctest}
>>> from attrs import make_class
>>> @define
... class C1:
...     x = field(type=int)
...     y = field()
>>> C2 = make_class("C2", {"x": field(type=int), "y": field()})
>>> fields(C1) == fields(C2)
True
>>> fields(C2).x.type
<class 'int'>
```

如果您传递一个名称与 {func}`~attrs.field` 映射的字典，您仍然可以控制属性，并且可以传递与 `@attrs.define` 相同的参数：

```{doctest}
>>> C = make_class("C", {"x": field(default=42),
...                      "y": field(default=Factory(list))},
...                repr=False)
>>> i = C()
>>> i  # 没有添加 repr！
<__main__.C object at ...>
>>> i.x
42
>>> i.y
[]
```

如果您需要动态创建一个类并且需要它是除 {class}`object` 之外的某个其他类的子类，请使用 `bases` 参数：

```{doctest}
>>> class D:
...    def __eq__(self, other):
...        return True  # 随意示例
>>> C = make_class("C", {}, bases=(D,), cmp=False)
>>> isinstance(C(), D)
True
```

有时，您希望类的 `__init__` 方法不仅仅执行初始化、验证等自动完成的任务。
为此，只需在类中定义一个 `__attrs_post_init__` 方法。
它将在生成的 `__init__` 方法结束时被调用。

```{doctest}
>>> @define
... class C:
...     x: int
...     y: int
...     z: int = field(init=False)
...
...     def __attrs_post_init__(self):
...         self.z = self.x + self.y
>>> obj = C(x=1, y=2)
>>> obj
C(x=1, y=2, z=3)
```

您可以从某些方法中排除单个属性：

```{doctest}
>>> @define
... class C:
...     user: str
...     password: str = field(repr=False)
>>> C("me", "s3kr3t")
C(user='me')
```

或者，若要影响生成的 `__repr__()` 方法如何格式化特定属性，请指定一个自定义可调用对象以替代 `repr()` 内置函数：

```{doctest}
>>> @define
... class C:
...     user: str
...     password: str = field(repr=lambda value: '***')
>>> C("me", "s3kr3t")
C(user='me', password=***)
```
