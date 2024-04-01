from setuptools import Extension, setup

if __name__ == "__main__":
    setup(
        name="pointers.py",
        packages=["pointers"],
        package_dir={"": "src"},
        ext_modules=[Extension("_pointers", ["./src/mod.c"])],
    )
