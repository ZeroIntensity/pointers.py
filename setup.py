import toml
from setuptools import Extension, setup

with open("./README.md") as f:
    long_desc: str = f.read()

if __name__ == "__main__":
    with open("./pyproject.toml", "r") as f:
        data = toml.load(f)
    setup(
        name="pointers.py",
        version="3.0.1",
        packages=["pointers"],
        project_urls=data["project"]["urls"],
        package_dir={"": "src"},
        license="MIT",
        ext_modules=[
            Extension(
                "_pointers",
                ["./src/mod.c"]
            )
        ],
    )
