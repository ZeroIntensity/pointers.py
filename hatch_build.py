import os
import shutil
import sysconfig
from contextlib import suppress
from distutils.extension import Extension
from glob import glob
from pathlib import Path

from find_libpython import find_libpython
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from hatchling.plugin import hookimpl
from setuptools._distutils.ccompiler import new_compiler

ext_modules = [
    Extension(
        "_pointers",
        include_dirs=["<header-file-directory>"],
        sources=glob("src/_pointers/*"),
    ),
]


class CustomBuildHook(BuildHookInterface):
    PLUGIN_NAME = "custom"

    def initialize(self, version: str, data: dict):
        self.clean()
        compiler = new_compiler()
        ext = os.path.join(self.root, "ext")
        lib = os.path.join(ext, "./ext/lib")

        # logic taken from distutils
        if sysconfig.get_config_var('Py_ENABLE_SHARED'):
            if not sysconfig.is_python_build():
                compiler.add_library_dir(sysconfig.get_config_var('LIBDIR'))
            else:
                compiler.add_library_dir('.')

        libpython_path = find_libpython()
        if not libpython_path:
            self.app.abort("failed to find libpython")

        compiler.add_library_dir(str(Path(libpython_path).parent.absolute()))

        compiler.add_include_dir(
            os.path.join(sysconfig.get_path("platstdlib"), "lib")
        )

        compiler.add_include_dir(sysconfig.get_path("include"))
        compiler.define_macro("PY_SSIZE_T_CLEAN")

        self.app.display_waiting("compiling _pointers")

        try:
            compiler.compile(
                glob("./src/mod.c"),
                output_dir=ext,
                extra_preargs=["-fPIC", "-v"]
            )
        except Exception:
            self.app.abort("failed to compile _pointers")

        self.app.display_success("successfully compiled _pointers")
        self.app.display_waiting("linking _pointers")

        files = []

        for root, _, fls in os.walk(ext):
            for i in fls:
                if i.endswith(".o"):
                    files.append(os.path.join(root, i))

        try:
            compiler.link_shared_lib(files, "_pointers", output_dir=lib)
        except Exception:
            self.app.abort("failed to link _pointers")

        self.app.display_success("successfully linked _pointers")

        with suppress(KeyError):
            data["force_include"][
                os.path.join(lib, "lib_pointers.so")
            ] = "src/_pointers.so"

        with suppress(KeyError):
            data["infer_tag"] = True

        with suppress(KeyError):
            data["pure_python"] = False

    def clean(self, *_):
        path = os.path.join(self.root, "ext")
        if os.path.exists(path):
            shutil.rmtree(path)


@hookimpl
def hatch_register_build_hook():
    return CustomBuildHook
