#!/usr/bin/env python3

from ppmgen import ppm_to_list, pam_from_list
from qoi import encode, decode

import sys

src = sys.argv[1]
out = sys.argv[2]
maxerr = int(sys.argv[3])

ppm_data = open(src, "rb").read()

input_bitmap = ppm_to_list(ppm_data)

qoi_bytes = encode(input_bitmap, maxerror = maxerr)

open(out, "wb").write(qoi_bytes)
