#!/usr/bin/env python3
"""Preserve original model; prepare one explicit structural research hypothesis."""
from pathlib import Path
import hashlib

BASE = Path(__file__).resolve().parent

def prepare():
    original = BASE / 'vendor/bc846b.lib'
    data = original.read_bytes()
    expected = '4912d730e03f4ea9dd83f779b09323942516c951a8fc1b2266a4b8b1c9397aed'
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError('Vendor model changed; audit before preparing a correction')
    before = b'Q2 11 2 33 MAIN 0.1364'
    after = b'Q2 11 2 3 MAIN 0.1364'
    if data.count(before) != 1:
        raise ValueError('Correction precondition failed')
    corrected = data.replace(before, after)
    path = BASE / 'vendor/bc846b_emitter_r1.lib'
    if path.exists() and path.read_bytes() != corrected:
        raise ValueError('Refusing to replace an existing correction')
    path.write_bytes(corrected)
    print('Prepared BC846B emitter-node research child; no parameter fitting or vendor approval asserted.')

if __name__ == '__main__':
    prepare()
