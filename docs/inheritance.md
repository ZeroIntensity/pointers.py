# Inheritance of Object behaviour

Pointers will inherit behaviours from the PyObject it points to:

### Item Subscription

The Pointer will inherit the behaviour for item retrieval from the referenced PyObject,
as such, the Pointer can be subscripted as a downstream behaviour at computation:

```py
import numpy as np
from pointers import to_ptr

x = np.arange(100).reshape(4, 25)
v = to_ptr(x)

>> v[(0, 4)]
>> 3 # does the same thing as above
```

### Item Assignment

The Pointer will respect the item assignment methods as well:

```py
import numpy as np
from pointers import to_ptr

x = np.arange(100).reshape(4, 25)
>>> x[0]
array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
       17, 18, 19, 20, 21, 22, 23, 24])

v = to_ptr(x)
v[(0, 4)] = 2

>>> v[0]
array([ 0,  1,  2,  3,  2,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
       17, 18, 19, 20, 21, 22, 23, 24]) # the pointer value has changed
>>> x[0]
array([ 0,  1,  2,  3,  2,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
       17, 18, 19, 20, 21, 22, 23, 24]) # the same for the original PyObject
```

### Magic methods

Pointers will inherit nearly all the magic methods, plus a few bonus ones specific to
Python Pointers:

```py

x = 1
y = 0

ptr1 =  to_ptr(x)
ptr2 = to_ptr(y)

>>> ptr1 & ptr2
0

>>> ptr1 | ptr2
1
```

Furthermore, this can be applied to major libraries such as Numpy:

```py
import numpy as np

x = np.array([1, 2, 3])
y = np.array([3, 4, 5])

ptr1 = to_ptr(x)
ptr2 = to_ptr(y)

 # ptr @ ptr
>>> ptr1 @ ptr2 # '@' is the matmul operator
26

 # ptr @ obj
>>> ptr1 @ y # also operates on the original object
26

 # obj @ ptr
>>> x @ ptr1 # however, non pointer objects can NOT refer to the values stored in pointers, therefore is raises:

>>> "ValueError: matmul: Input operand 1 does not have enough dimensions (has 0, gufunc core with signature (n?,k),(k,m?)->(n?,m?) requires 1)"

```
### Applying functions
Since we are already using the '<<' and '>>' operators - we should find a way to apply functions to pointers if we need that (because
  why not make things more complicated). As such, there is a special method unique to pointers which allows you to apply a function to a
  Python pointer and reassign the pointer to that value. However; the drawback of this is that you must be *extremely* careful when
  managing datatypes and the outputs to those functions:

```py
x = 4

ptr = to_ptr(x)
ptr <<= lambda y: y ** 2 # expects int, outputs int - using '<<=' to apply on pointer

>>> ~ptr
16 # 4 squared

```

### Caveats

Item methods are only inherited by Pointer and Malloc Pointers,
attempting to reference a CallocPointer as such will return:

```py
from pointers import calloc

c = calloc(2, 120)
c << ['a', 'b', 'c']
c[0] = 5

>>> "TypeError: 'CallocPointer' object does not support item assignment"
```

Instead, it is proper form to create an object directly, and reference the object itself.
Note though, that the Calloc chunk will only respect assignment if the object's size
is equal to or lesser than the original chunk + the reassigned object:

```py
from pointers import calloc

c = calloc(2, 120)
obj = ['a', 'b', 'c']
c << obj
obj[0] = 5

>> ~c
>> [5, 'b', 'c']
```
