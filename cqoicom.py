#!/usr/bin/env python3

from ppmgen import ppm_to_list, pam_from_list
from qoi import encode, decode

import sys

if len(sys.argv) < 3:
    print(f"""
USAGE:
{sys.argv[0]} input.[ppm/qoi] output.qoi <max_error [float], default: 0>
""")
    sys.exit()

src = sys.argv[1]
out = sys.argv[2]
if len(sys.argv) > 3:
    maxerr = float(sys.argv[3])
else:
    maxerr = 0

ppm_data = open(src, "rb").read()

if src.endswith(".qoi"):
    input_bitmap = decode(ppm_data)
else:
    input_bitmap = ppm_to_list(ppm_data)

qoi_bytes = encode(input_bitmap, maxerror = maxerr)

open(out, "wb").write(qoi_bytes)
