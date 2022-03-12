from setuptools import setup

with open('./README.md') as f:
    long_desc: str = f.read()

if __name__ == "__main__":
    setup(
        name = "pointers.py",
        version = "1.1.0",
        author = "ZeroIntensity",
        author_email = "<zintensitydev@gmail.com>",
        description = "Bringing the hell of pointers to Python.",
        long_description_content_type = "text/markdown",
        long_description = long_desc,
        py_modules = ['pointers'],
        keywords = ['python', 'pointers'],
        install_requires = ['typing_extensions'],
        classifiers = [
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11"
        ],
        license = "MIT",
        project_urls = {
            "Source": "https://github.com/ZeroIntensity/pointers.py"
        }
    )