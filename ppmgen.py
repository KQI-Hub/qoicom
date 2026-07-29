def ppm_from_list(bitmap, desc = None):
    ppmhead = "P6\n" # raw format
    ppmbody = bytearray() # byte array

    if desc:
        ppmhead += "# {desc}\n"

    ppmhead += f"{len(bitmap[0])} {len(bitmap)}\n"
    ppmhead += "255\n"

    for row in bitmap:
        for pixel in row:
            if pixel is None:
                ppmbody.append(255)
                ppmbody.append(0)
                ppmbody.append(255)

            else:
                ppmbody.append(pixel[0])
                ppmbody.append(pixel[1])
                ppmbody.append(pixel[2])

    return ppmhead.encode() + bytes(ppmbody)

def pam_from_list(bitmap):
    pamhead = f"P7\nWIDTH {len(bitmap[0])}\nHEIGHT {len(bitmap)}\nDEPTH 4\nMAXVAL 255\nTUPLTYPE RGB_ALPHA\nENDHDR\n" # PAM format
    pambody = bytearray() # byte array
    for row in bitmap:
        for pixel in row:
            if pixel is None:
                pambody.append(0)
                pambody.append(0)
                pambody.append(0)
                pambody.append(0)
            else:
                pambody.append(pixel[0])
                pambody.append(pixel[1])
                pambody.append(pixel[2])
                if len(pixel) > 3:
                    pambody.append(pixel[3])
                else:
                    pambody.append(255) # slightly heavier but allows for non-transparent images to output to an RGBA PAM

    return pamhead.encode() + bytes(pambody)

def pgm_from_list(bitmap, desc = None):
    pgmhead = "P5\n" # raw format
    pgmbody = bytearray() # byte array

    if desc:
        pgmhead += "# {desc}\n"

    pgmhead += f"{len(bitmap[0])} {len(bitmap)}\n"
    pgmhead += "255\n"

    for row in bitmap:
        for pixel in row:
            pgmbody.append(pixel)

    return pgmhead.encode() + bytes(pgmbody)

def ppm_to_list(data: bytes):
    if not data.startswith(b'P6') and not data.startswith(b'P5'):
        raise Exception("Unsupported PPM!")
    gray = False
    if data.startswith(b"P5"):
        gray = True
    head = data.split(b"\n", 4)
    one = 1
    if head[1].decode('ascii').startswith("#"):
        one = 2
    res = head[one].decode('ascii').split(" ")
    width = int(res[0])
    height = int(res[1])
    tulmax = head[one+1].decode('ascii')
    if not tulmax == "255":
        raise Exception("Unsupported PPM!")
    if one == 1:
        bmpmap = data.split(b"\n", 3)[3]
    else:
        bmpmap = head[4]
    bitmap = []
    for h in range(height):
        bitmap.append([])
        for p in range(width):
            ligma = (h*width)+p
            if gray:
                bitmap[h].append(bmpmap[ligma])
            else:
                bitmap[h].append(( bmpmap[ligma*3] , bmpmap[(ligma*3)+1] , bmpmap[(ligma*3)+2] ))
    
    return bitmap

def blank_bitmap_list(width, height):
    frame = []
    blankline = []
    for _ in range(width):
        blankline.append(None)
    for _ in range(height):
        frame.append(blankline[:])
    return frame
