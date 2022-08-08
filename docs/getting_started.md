# Getting Started

## Installation

To get started with pointers.py, install the library:

### Linux/macOS

```
python3 -m pip install -U pointers.py
```

### Windows

```
py -3 -m pip install -U pointers.py
```

**Python 3.6+ is required**

## Creating a pointer

Now that you have installed the library, we can start creating pointers.

Start with importing `to_ptr`, and then calling it on a value:

```py
from pointers import to_ptr

val = "hello world!"
ptr = to_ptr(val) # <pointer to str object at [address]>
```

Variable `ptr` gets assigned to type `pointers.Pointer[str]`.

This is equivalent to the following C++ code:

```cpp
#include <string>

using std::string;

int main() {
    string val { "hello world!" };
    string* ptr { &val };
    return 0;
}
```

Or the following C code:

```c
int main() {
    char* val = "hello world!";
    char** ptr = &val;
    return 0;
}
```

## Using `_`

Instead of using `to_ptr`, you can use pointers.py's `_` object to replicate C/C++'s address-of operator:

```py
from pointers import _

ptr = _&"test"
```

## Decaying

While the pointer API is cool, having `to_ptr` everywhere isn't exactly great.

This is especially ugly when using functions:

```py
from pointers import to_ptr, Pointer
from typing import List, Any

def address_sum(first: Pointer[Any], second: Pointer[Any]) -> List[int]:
    return first.address + second.address # we will talk about other pointer attributes later

print(address_sum(to_ptr("abc"), to_ptr("123"))) # this can get out of hand very quickly!
```

Luckily, there is a `decay` decorator, that automatically converts function arguments into pointers:

```py
@decay
def address_sum(first: Pointer[Any], second: Pointer[Any]) -> List[int]:
    return first.address + second.address

print(address_sum("abc", "123")) # much better
```

The `decay` decorator will **only** decay arguments hinted as `Pointer`. For example:

```py
@decay
def address_sum(first, second) -> List[int]:
    return first.address + second.address # error: str has no attribute address

print(address_sum("abc", "123")) # the data doesnt get decayed!
```
