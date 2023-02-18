try:
    import _pointers
except ImportError as e:
    raise ImportError("_pointers has not been built, did you forget to compile it?") from e

__version__ = "3.0.0"
__license__ = "MIT"
