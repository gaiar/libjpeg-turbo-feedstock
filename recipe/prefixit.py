# coding=utf-8
"""
Prefix global symbols in libjpeg.a so we avoid any clash with symbols from jpeg >= 9.

Usage:
  TURBO_PATH=/where/your/compiled/turbo/lives python prefixit.py
"""
from __future__ import print_function, division

import os
import os.path as op
import subprocess

MY_PATH = op.dirname(__file__)
TURBO_PATH = os.getenv('TURBO_PATH', op.join(MY_PATH, 'turbo-cf'))

TURBO_LIB_PATH = op.join(TURBO_PATH, 'lib')
A_FILE = op.join(TURBO_LIB_PATH, 'libjpeg.a')
if not op.isfile(A_FILE):
    A_FILE = op.join(TURBO_LIB_PATH, 'libjpeg-turbo-prefixed', 'libturbojpeg.a')

TURBO_INCLUDE_PATH = op.join(TURBO_PATH, 'include')
H_FILE = op.join(TURBO_INCLUDE_PATH, 'jpeglib.h')
if not op.isfile(H_FILE):
    H_FILE = op.join(TURBO_INCLUDE_PATH, 'libjpeg-turbo-prefixed', 'jpeglib.h')

FAILED_NOT_FOUND_SYMBOL = "jpeg_resync_to_restart"


def prefix_global_turbo_symbols(a_file=A_FILE, h_file=H_FILE, prefix='turbo_'):

    # Collect symbols to prefix.
    # The narrower this is without resulting in symbol clash, the better.
    only_rename_types = ('D', 'R', 'T')  # ('d', 'r', 't') should not be exported anyway
    forbidden_prefixes = ('_', '.')
    symbols_to_rename = []

    for line in subprocess.check_output(['nm', '-A', a_file]).decode('utf-8').splitlines():
        parts = line.split()
        if len(parts) == 2:
            fn, symbol_type = parts
        else:
            fn, symbol_type, symbol_name = parts
        assert not symbol_name.startswith(prefix)
        if not any(map(symbol_name.startswith, forbidden_prefixes)) and symbol_type in only_rename_types:
            symbols_to_rename.append(symbol_name)
    symbols_to_rename = sorted(set(symbols_to_rename))

    # Generate new .a
    print('Prefixing symbols in %s' % a_file)
    symbols_map_file = op.join(MY_PATH, 'redefines.txt')
    with open(symbols_map_file, 'wt') as writer:
        for symbol_name in symbols_to_rename:
            writer.write('%s %s\n' % (symbol_name, prefix + symbol_name))
    subprocess.check_call(['objcopy',
                           '--redefine-syms=%s' % symbols_map_file,
                           a_file,
                           a_file])
    os.unlink(symbols_map_file)

    # Generate new .h
    # Amazing refactoring tool...
    # If this breaks it, use a proper parser

    print('Generating kinda wrapping header for %s' % h_file)

    with open(h_file, 'rt') as reader:
        htxt = reader.read()
        renamed_symbols = []
        # These won't be renamed in the header file
        # (they actually *should not* appear there)
        banned = ('jpeg_destroy',)
        for symbol_name in symbols_to_rename:
            if symbol_name in htxt and symbol_name not in banned:
                renamed_symbols.append(symbol_name)
                htxt = htxt.replace(symbol_name, prefix + symbol_name)

        # Obvious problem with prefixes; for example:
        #   jpeg_destroy, jpeg_destroy_compress and jpeg_destroy_decompress all exist in the lib
        #   jpeg_destroy is a prefix
        #   jpeg_destroy is not part of the public API in libjpeg.h
        # This is better solved with "banned" (takes care of any such problem in 1.5.3)
        # Ugly workaround, proper one is to parse and only replace symbols
        prefixprefix = prefix + prefix
        while prefixprefix in htxt:
            htxt = htxt.replace(prefixprefix, prefix)

        # Create aliases and massage the header
        # We try to restrict only to public API (see "renamed_symbols")
        # (should maybe even restrict to what used by opencv using one of
        # those tools that introspect ELFs and tells you the minimum set of symbols
        # used from a library). Knowing that, we should probably provide a linker
        # version script...
        htxt = htxt.replace('JPEGLIB_H', 'TURBOJPEGLIB_H')
        lines = htxt.splitlines(keepends=False)
        aliases = ['#define %s %s' % (symbol_name, prefix + symbol_name) for symbol_name in renamed_symbols]
        lines = (lines[:-1] +
                 ['\n/* The original function names are now brutally forced to be aliases. */\n'] +
                 aliases +
                 [''] +
                 [lines[-1]])
        htxt = '\n'.join(lines)

        # Create a new header file and also use it to replace jpeglib.h
        new_header = op.join(op.dirname(h_file), 'turbojpeglib.h')
        with open(new_header, 'wt') as writer:
            writer.write(htxt)
        os.unlink(h_file)
        os.symlink(op.basename(new_header), h_file)


if __name__ == '__main__':
    prefix_global_turbo_symbols()
