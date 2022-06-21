# Contribution

If you would like to contribute to pointers.py, just make a pull request with your changes.

Any pull request should include the following:

- Type safe and provides type annotations
- PEP 8 compliant code
- Passes tests specified in the [tests](https://github.com/ZeroIntensity/pointers.py/tree/master/tests) directory
- Documentation updated accordingly

## Running tests

You can install the tests by installing dependencies in the `requirements_dev.txt` file:

```
pip install -r requirements_dev.txt
```

### Mypy

Mypy type checks the code.

You can run it with the following command:

```
python3 -m mypy src
```

### Flake8

Flake8 ensures that the codebase is compliant to [PEP 8](https://peps.python.org/pep-0008/).

Heres how you run it:

```
python3 -m flake8 src
```

### Pytest

Pytest handles all unit tests for pointers.py

Run it by simply using:

```
python3 -m pytest
```

### Tox

Tox runs all 3 of the above in different python environments:

```
python3 -m tox
```

Please note that running tox is extremely slow and can take several minutes.

## Running documentation

Start with installing [mkdocs](https://pypi.org/project/mkdocs/):

```
python3 -m pip install -U mkdocs
```

To build the documentation, run the following command:

```
python3 -m mkdocs build
```

This will build the site in the `site/` directory.

However, constantly building can be annoying, so you can use `serve` instead:

```
python3 -m mkdocs serve
```

This will automatically rebuild when you change a file.
