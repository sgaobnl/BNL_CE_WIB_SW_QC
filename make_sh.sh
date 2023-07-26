#!/bin/bash

find . -type f -exec touch {} +
mkdir build
make
