try:
    import _pointers
except ImportError as e:
    raise ImportError(
        "_pointers has not been built, did you forget to compile it?"
    ) from e


if __import__("sys").implementation.name != "cpython":
    raise ImportError("pointers.py is only supported on cpython")


from .base_pointer import *
from .exceptions import *
from .pyobject_pointer import *
from .util import *

__version__ = "3.0.0"
__license__ = "MIT"
__author__ = "ZeroIntensity"
