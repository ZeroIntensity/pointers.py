# Bindings

Pointers.py provides Python bindings for most of the C standard library.

To use one, import it from the `pointers.bindings` module:

```py
from pointers.bindings import strlen

print(strlen('hello')) # 5
```
