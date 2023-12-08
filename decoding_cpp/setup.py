import os
from glob import glob
from setuptools import setup
# from Cython.Build import cythonize
from pybind11.setup_helpers import Pybind11Extension, build_ext

cwd = os.getcwd()

ext_modules = [
    Pybind11Extension(
        "_daq_rawdatautils_py",
        sorted(glob("rawdatautils\\pybindsrc\\*.cpp")),  # Sort source files for reproducibility
        # include_dirs=["rawdatautils\\include\\rawdatautils", "daqdataformats\\include\\daqdataformats", "fddetdataformats\\include\\fddetdataformats", "detdataformats\\include\\detdataformats"],
        include_dirs=[cwd+"\\rawdatautils\\include", cwd+"\\daqdataformats\\include", cwd+"\\fddetdataformats\\include", cwd+"\\detdataformats\\include"],
        extra_compile_args=["/std:c++17"],
    ),
]

setup(
    name = "_daq_rawdatautils_py",
    # ext_modules=cythonize(ext_modules,build_dir="./build_tmp"),
    ext_modules=ext_modules,
    python_requires=">=3.7",
    package_data={"": ["*.h"]} 
)

# extension = Extension(
        # "primesieve",
        # ["primesieve/primesieve.cpp"],
        # include_dirs=["lib/primesieve/include", "lib/primesieve/include/primesieve"],
        # language="c++",
        # )