#!/bin/bash
#
# See:
#   https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/BUILDING.md
#

#
# How to add proper version info, so opencv getBuildInfo can display it?
# Need to check with opencv, and probably add it like:
#   https://stackoverflow.com/questions/1638207/how-to-store-a-version-number-in-a-static-library
#
#cd libjpeg-turbo-1.5.0/
#mkdir build
#autoreconf -fiv
#cd build
#export CFLAGS="-mcpu=cortex-a7 -mfpu=neon-vfpv4 -ftree-vectorize -mfloat-abi=hard -fPIC -O3"
#export CXXFLAGS="-mcpu=cortex-a7 -mfpu=neon-vfpv4 -ftree-vectorize -mfloat-abi=hard -fPIC -O3"
#sh <path_to_the_source_code>/configure

TURBO_PREFIX=${PREFIX}/lib/libjpeg-turbo

mkdir build
autoreconf -fiv
cd build

export CFLAGS="-mcpu=cortex-a7 -mfpu=neon-vfpv4 -ftree-vectorize -mfloat-abi=hard -fPIC -O3"
export CXXFLAGS="-mcpu=cortex-a7 -mfpu=neon-vfpv4 -ftree-vectorize -mfloat-abi=hard -fPIC -O3"

cmake -LAH \
  -DCMAKE_RULE_MESSAGES=ON                                           \
  -DCMAKE_VERBOSE_MAKEFILE=OFF                                       \
  -G"Unix Makefiles"                                                 \
  -DCMAKE_BUILD_TYPE=Release                                         \
  -DCMAKE_ASM_NASM_COMPILER=yasm                                     \
  -DCMAKE_POSITION_INDEPENDENT_CODE=ON                               \
  -DREQUIRE_SIMD=ON                                                  \
  -DENABLE_STATIC=ON                                                 \
  -DENABLE_SHARED=ON                                                 \
  -DWITH_JPEG8=ON                                                    \
  -DWITH_TURBOJPEG=ON                                                \
  -DCMAKE_INSTALL_PREFIX=${TURBO_PREFIX}                             \
  -DCMAKE_INSTALL_LIBDIR="${TURBO_PREFIX}/lib"                       \
  ..

make -j${CPU_COUNT} ${VERBOSE_AT}
make test
make install

# Prefix symbols to avoid clashing with libjpeg 9
# Trying to play with the visibility of the symbols + opencv
# is quite complicated, so to my mind this is the safest
# and more straightforward option.
TURBO_PATH=${TURBO_PREFIX} python ${RECIPE_DIR}/prefixit.py

# Should happen, but do not ATM:
#   1- Compile the binaries against the prefixed library
#   2- Then rerun the tests against the prefixed library
#      Note: currently they pass, we would only miss:
# 	      150 - jpegtran-shared-crop (Failed)
#         151 - jpegtran-shared-crop-cmp (Failed))
#   3- Run specific tests for the prefixed version of the lib
