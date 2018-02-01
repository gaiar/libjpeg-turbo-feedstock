#!/bin/bash

#
# See:
#   https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/BUILDING.md

#
# Set at CFLAGS any optimization needed.
# N.B. only SSE extensions are used up to libjpeg-turbo 1.5.x; AVX coming in 1.6
#

#
# How to add proper version info, so opencv getBuildInfo can display it?
# Need to check with opencv, and probably add it like:
#   https://stackoverflow.com/questions/1638207/how-to-store-a-version-number-in-a-static-library
#

autoreconf -fiv

_build=$(date --utc --date="@${SOURCE_DATE_EPOCH:-$(date +%s)}" +%Y%m%d)

./configure --prefix=${PREFIX} \
    --bindir=${PREFIX}/bin/libjpeg-turbo-prefixed \
    --includedir=${PREFIX}/include/libjpeg-turbo-prefixed \
    --libdir=${PREFIX}/lib/libjpeg-turbo-prefixed \
    --enable-shared=no \
    --enable-static=yes \
    CFLAGS="-fPIC -O3" \
    --with-build-date=${_build} \
    NASM=yasm
make
make check

make install

# Make a version of the static library with prefixed symbols to avoid clashing with libjpeg 9
# Trying to play with the visibility of the symbols is quite complicated, so
# to my mind this is the safest and more straightforward option.
export TURBO_PATH=${PREFIX}
python ${RECIPE_DIR}/prefixit.py

# I do not know how to avoid these to be generated
# (they are even if adding --without-jpeg8 or not adding anything)
rm -Rf ${PREFIX}/bin/libjpeg-turbo-prefixed
rm -f ${PREFIX}/lib/libjpeg-turbo-prefixed/libjpeg.a
rm -f ${PREFIX}/lib/libjpeg-turbo-prefixed/libjpeg.la
rm -f ${PREFIX}/lib/libjpeg-turbo-prefixed/pkgconfig/libjpeg.pc

# These might be out of sync with the new names in the static lib; resync if needed
rm -f ${PREFIX}/include/libjpeg-turbo-prefixed/turbojpeg.h
