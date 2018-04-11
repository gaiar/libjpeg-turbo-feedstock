# coding=utf-8
"""
Prefix global symbols in libjpeg turbo so we avoid clashes with symbols from jpeg >= 9.

Usage:
  TURBO_PATH=/where/your/compiled/turbo/lives python prefixit.py
"""
from __future__ import print_function, division

import glob
import os
import shutil

import os.path as op
import subprocess

MY_PATH = op.dirname(__file__)
TURBO_PATH = os.getenv('TURBO_PATH', op.join(MY_PATH, 'turbo-cf'))

PREFIXED_TURBO_PATH = op.join(TURBO_PATH, 'prefixed')
os.makedirs(PREFIXED_TURBO_PATH)
shutil.copytree(op.join(TURBO_PATH, 'include'), op.join(PREFIXED_TURBO_PATH, 'include'), symlinks=True)
shutil.copytree(op.join(TURBO_PATH, 'lib'), op.join(PREFIXED_TURBO_PATH, 'lib'), symlinks=True)

LIBJPEG_A_FILE = op.join(PREFIXED_TURBO_PATH, 'lib', 'libjpeg.a')
LIBJPEG_SO_FILE = op.realpath(op.join(PREFIXED_TURBO_PATH, 'lib', 'libjpeg.so'))
LIBJPEG_H_FILE = op.join(PREFIXED_TURBO_PATH, 'include', 'jpeglib.h')
LIBJPEG_H_FINAL_FILE = op.join(PREFIXED_TURBO_PATH, 'include', 'turbojpeglib.h')

LIBTURBOJPEG_A_FILE = op.join(PREFIXED_TURBO_PATH, 'lib', 'libturbojpeg.a')
LIBTURBOJPEG_SO_FILE = op.realpath(op.join(PREFIXED_TURBO_PATH, 'lib', 'libturbojpeg.so'))
LIBTURBOJPEG_H_FILE = op.join(PREFIXED_TURBO_PATH, 'include', 'turbojpeg.h')

PREFIX = 'turbo_'


# --- Collect symbols to prefix.
# The narrower this is without resulting in symbol clash, the better.

ONLY_RENAME_TYPES = ('D', 'R', 'T')  # ('d', 'r', 't') should not be exported anyway
FORBIDDEN_PREFIXES = ('_', '.')
symbols_to_rename = []

print('Collecting libjpeg public symbols')
for line in subprocess.check_output([os.environ.get('NM', 'nm'),
                                     '-A',
                                     LIBJPEG_A_FILE]).decode('utf-8').splitlines():
    parts = line.split()
    if len(parts) == 2:
        fn, symbol_type = parts
    else:
        fn, symbol_type, symbol_name = parts
        assert not symbol_name.startswith(PREFIX)
        if not any(map(symbol_name.startswith, FORBIDDEN_PREFIXES)) and symbol_type in ONLY_RENAME_TYPES:
            symbols_to_rename.append(symbol_name)
symbols_to_rename = sorted(set(symbols_to_rename))

symbols_map_file = op.join(MY_PATH, 'redefines.txt')
with open(symbols_map_file, 'wt') as writer:
    for symbol_name in symbols_to_rename:
        writer.write('%s %s\n' % (symbol_name, PREFIX + symbol_name))

# --- Generate new .a(s)

print('Prefixing symbols in static libraries')
objcopy = 'x86_64-conda_cos6-linux-gnu-objcopy'  # objcopy
for a_file in (LIBJPEG_A_FILE, LIBTURBOJPEG_A_FILE):
    print('Prefixing symbols in %s' % a_file)
    subprocess.check_call([
        os.environ.get('OBJCOPY', 'objcopy'),
        '--redefine-syms=%s' % symbols_map_file,
        a_file,
        a_file
    ])

os.unlink(symbols_map_file)

# --- Generate new .so(s)
# Of course, the original is more sophisticated (e.g. version scripts for visibility)
# Go for more sophistication if problems arise

print('Prefixing symbols in dynamic libraries')
for so_file, a_file in [(LIBJPEG_SO_FILE, LIBJPEG_A_FILE), (LIBTURBOJPEG_SO_FILE, LIBTURBOJPEG_A_FILE)]:
    print('Prefixing symbols in %s' % so_file)
    os.unlink(so_file)
    subprocess.check_call([
        os.environ.get('GCC', 'gcc'),
        '-shared',
        '-o', so_file,
        '-Wl,--whole-archive', a_file,
        '-Wl,--no-whole-archive'],
        env=os.environ)

# --- Generate new .h
# Amazing refactoring tool...
# If this breaks it, use a proper parser

print('Generating kinda wrapping header for %s' % LIBJPEG_H_FILE)
with open(LIBJPEG_H_FILE, 'rt') as reader:
    htxt = reader.read()
    renamed_symbols = []
    # These won't be renamed in the header file
    # (they actually *should not* appear there)
    banned = ('jpeg_destroy',)
    for symbol_name in symbols_to_rename:
        if symbol_name in htxt and symbol_name not in banned:
            renamed_symbols.append(symbol_name)
            htxt = htxt.replace(symbol_name, PREFIX + symbol_name)

    # Obvious problem with prefixes; for example:
    #   jpeg_destroy, jpeg_destroy_compress and jpeg_destroy_decompress all exist in the lib
    #   jpeg_destroy is a prefix
    #   jpeg_destroy is not part of the public API in libjpeg.h
    # This is better solved with "banned" (takes care of any such problem in 1.5.3)
    # Ugly workaround, proper one is to parse and only replace symbols
    prefixprefix = PREFIX + PREFIX
    while prefixprefix in htxt:
        htxt = htxt.replace(prefixprefix, PREFIX)

    # Create aliases and massage the header
    # We try to restrict only to public API (see "renamed_symbols")
    # (should maybe even restrict to what used by opencv using one of
    # those tools that introspect ELFs and tells you the minimum set of symbols
    # used from a library). Knowing that, we should probably provide a linker
    # version script with proper symbol visibility
    htxt = htxt.replace('JPEGLIB_H', 'TURBOJPEGLIB_H')
    lines = htxt.splitlines(False)
    aliases = ['#define %s %s' % (symbol_name, PREFIX + symbol_name) for symbol_name in renamed_symbols]
    lines = (lines[:-1] +
             ['\n/* The original function names are now brutally forced to be aliases. */\n'] +
             aliases +
             [''] +
             [lines[-1]])
    htxt = '\n'.join(lines)

    # Replace jpeglib.h; make it clear it is not the original
    with open(LIBJPEG_H_FINAL_FILE, 'wt') as writer:
        writer.write(htxt)
    os.unlink(LIBJPEG_H_FILE)
    os.symlink(op.basename(LIBJPEG_H_FINAL_FILE), LIBJPEG_H_FILE)

# --- Fix pkgconfig files
print('Fixing pkgconfig files...')
for pc_file in glob.glob(op.join(PREFIXED_TURBO_PATH, 'lib', 'pkgconfig', '*.pc')):
    print('Fixing %s' % pc_file)
    with open(pc_file, 'rt') as reader:
        # Nasty and effective
        fixed = reader.readlines()
        fixed[0] = 'prefix=/opt/anaconda1anaconda2anaconda3/lib/libjpeg-turbo/prefixed\n'
        fixed[1] = 'exec_prefix=/opt/anaconda1anaconda2anaconda3/lib/libjpeg-turbo/prefixed\n'
        fixed[2] = 'libdir=/opt/anaconda1anaconda2anaconda3/lib/libjpeg-turbo/prefixed/lib/\n'
        fixed[3] = 'includedir=/opt/anaconda1anaconda2anaconda3/lib/libjpeg-turbo/prefixed/include\n'
        with open(pc_file, 'wt') as writer:
            writer.writelines(fixed)
