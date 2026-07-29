from ppmgen import ppm_to_list, pam_from_list
from qoi import encode, decode

ppm_data = open("rtx0.ppm", "rb").read()

input_bitmap = ppm_to_list(ppm_data)

qoi_bytes = encode(input_bitmap)

open("rtx0-encoded.qoi", "wb").write(qoi_bytes)

qoi_data = open("rtx0-encoded.qoi", "rb").read()

bitmap_list = decode(qoi_data)

ppm = pam_from_list(bitmap_list)

open("rtx0-decoded.pam", "wb").write(ppm)