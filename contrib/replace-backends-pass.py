#!/usr/bin/env python3

"""
This script edits your backends conf file by replacing stuff like:

[bnporc21]
_module = bnporc
website = pp
login = 123456
password = 78910

with:

[bnporc21]
_module = bnporc
website = pp
login = 123456
password = `pass show weboob/bnporc21`
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile

FILE = os.getenv('WEBOOB_BACKENDS') or os.path.expanduser('~/.config/weboob/backends')

if not os.path.exists(FILE):
    print('the backends file does not exist')
    sys.exit(os.EX_NOINPUT)

if not shutil.which('pass'):
    print('the "pass" tool could not be found')
    sys.exit(os.EX_UNAVAILABLE)

errors = 0
seen = set()

with open(FILE) as inp:
    with tempfile.NamedTemporaryFile('w', delete=False, dir=os.path.dirname(FILE)) as outp:
        for line in inp:
            line = line.strip()

            mtc = re.match(r'password\s*=\s*(\S.*)$', line)
            if mtc and not mtc.group(1).startswith('`'):
                cmd = ['pass', 'insert', 'weboob/%s' % backend]
                stdin = 2 * ('%s\n' % mtc.group(1))

                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                proc.communicate(stdin.encode('utf-8'))
                if proc.returncode == 0:
                    print('password = `pass show weboob/%s`' % backend, file=outp)
                    continue
                else:
                    errors += 1
                    print('warning: could not store password for backend %r' % backend)

            mtc = re.match(r'\[(.+)\]', line)
            if mtc:
                backend = mtc.group(1)
                if backend in seen:
                    print('error: backend %r is present multiple times' % backend)
                    sys.exit(os.EX_DATAERR)
                seen.add(backend)

            print(line, file=outp)

os.rename(outp.name, FILE)

if errors:
    print('%d errors were encountered when storing passwords securely' % errors)
    sys.exit(2)
