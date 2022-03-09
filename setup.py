from setuptools import setup

with open('./README.md') as f:
    long_desc: str = f.read()

if __name__ == "__main__":
    setup(
        name = "pointers.py",
        version = "1.0.0",
        author = "ZeroIntensity",
        author_email = "<zintensitydev@gmail.com>",
        description = "Bringing the hell of pointers to Python.",
        long_description_content_type = "text/markdown",
        long_description = long_desc,
        py_modules = ['templates'],
        keywords = ['python', 'pointers'],
        classifiers = [
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11"
        ],
        license = "MIT",
        urls = {
            "Repo": "https://github.com/ZeroIntensity/pointers.py"
        }
    )