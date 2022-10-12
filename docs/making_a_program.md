# Making a Program

Now that we've learned how to use pointers.py, lets build a small script to make `1 == 2`, and then revert our changes (make `1 != 2`).

Lets start out with creating a pointer to `1`, and then moving `2` to it:

```py
from pointers import _

ptr = _&1
ptr <<= 2

assert 1 == 2
```

Running this will work just fine, and no `AssertionError` will be raised.

But how do we revert our changes now? `1` has been overwritten, so we can't just move a `1` back into the pointer.

If you want, you can take a second to think about how to do it.

---

We can cache our `1` by using memory allocation. Since the `1` will be copied to its own memory space, it won't get affected by overwriting `1`.

You can try this out yourself.

```py
from pointers import malloc, _

one = malloc(28)
one <<= 1

ptr = _&1
ptr <<= 2

print(1, ~one)
```

Running this will output `2 1`!

Ok, lets allocate a `1` before we overwrite it:

```py
from pointers import malloc, free, _

cache = malloc(28)
cache <<= 1

ptr = _&1
```

Then, lets move the allocated `1` back into our pointer at the end of the program:

```py
ptr = _&1
ptr <<= 2

assert 1 == 2

ptr <<= ~cache
assert 1 != 2
```

Don't forget to free the memory as well:

```py
free(cache)
```

Here's the final result:

```py
from pointers import malloc, free, _

cache = malloc(28)
cache <<= 1

ptr = _&1
ptr <<= 2

assert 1 == 2

ptr <<= ~cache
assert 1 != 2
free(cache)
```

**Note:** This may not work depending on your build of CPython.

Congratulations, you have written a working program with pointers.py!
