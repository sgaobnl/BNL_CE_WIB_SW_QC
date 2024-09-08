#!/bin/sh

export WRKDIR=$PWD

# git clone, build, and install pybind11
git clone git@github.com:pybind/pybind11.git
mkdir pybind11_build pybind11_install
cd pybind11_build
cmake -DCMAKE_INSTALL_PREFIX=$WRKDIR/pybind11_install $WRKDIR/pybind11
make check -j6
make install

# Assuming you already have anaconda, modified your makefile to point to the corresponding python version, and activated the conda environment
cd $WRKDIR
mkdir build
python setup.py build --build-lib=./build
make -j6
