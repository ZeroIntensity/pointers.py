from setuptools import Extension, setup

if __name__ == "__main__":
    setup(
        ext_modules=[Extension("_pointers", ["./src/mod.c"])],
        license="MIT",
    )
