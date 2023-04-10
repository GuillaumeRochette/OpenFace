#!/bin/bash

mkdir build
cd build
cmake -DCMAKE_CXX_COMPILER=g++ -DCMAKE_C_COMPILER=gcc -DCMAKE_BUILD_TYPE=RELEASE ..
make -j$((`nproc`+1))
cd ..
