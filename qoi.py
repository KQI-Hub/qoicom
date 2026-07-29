from bittools import byte_to_boollist, boollist_to_int_var, intclamp, generate_boollist
from ppmgen import blank_bitmap_list

def encode(image: list):
    header = bytearray(b"qoif")
    width = len(image[0])
    height = len(image)
    header.extend(width.to_bytes(4, 'big'))
    header.extend(height.to_bytes(4, 'big'))
    header.extend(int(4).to_bytes(1, 'little'))
    header.extend(int(0).to_bytes(1, 'little'))

    last_pixel = (0,0,0,255)
    runcounter = 0
    index_table = [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)] # initialize to blank

    footer = b"\x00\x00\x00\x00\x00\x00\x00\x01"

    bitstream = bytearray()
    for y in range(height):
        for x in range(width):
            current_pixel = image[y][x]
            if len(current_pixel) == 3:
                current_pixel+=(255,)

            index_position = (current_pixel[0] * 3 + current_pixel[1] * 5 + current_pixel[2] * 7 + current_pixel[3] * 11) % 64
            if last_pixel == current_pixel:
                if runcounter == 62:
                    bitstream.append(191+runcounter)
                    runcounter = 1
                else:
                    runcounter += 1
            else:
                if runcounter:
                    bitstream.append(191+runcounter)
                    runcounter = 0

                dr = (current_pixel[0]-last_pixel[0])
                dg = (current_pixel[1]-last_pixel[1])
                db = (current_pixel[2]-last_pixel[2])
                dr_dg = dr-dg
                db_dg = db-dg

                if current_pixel == index_table[index_position]:
                    byte = [False, False]
                    byte.extend(generate_boollist(index_position, 6))
                    bitstream.append(boollist_to_int_var(byte))
                elif (dr > -3 and dr < 2) and (dg > -3 and dg < 2) and (db > -3 and db < 2) and current_pixel[3] == last_pixel[3]:
                    val_list = [False, True]
                    val_list.extend(generate_boollist(dr+2, 2))
                    val_list.extend(generate_boollist(dg+2, 2))
                    val_list.extend(generate_boollist(db+2, 2))
                    bitstream.append(boollist_to_int_var(val_list))
                elif (dg > -33 and dg < 32) and (dr_dg > -9 and dr_dg < 8) and (db_dg > -9 and db_dg < 8) and current_pixel[3] == last_pixel[3]:
                    val_list = [True, False]
                    val_list.extend(generate_boollist(dg+32, 6))
                    bitstream.append(boollist_to_int_var(val_list))
                    val_list_2 = generate_boollist(dr_dg+8, 4)
                    val_list_2.extend(generate_boollist(db_dg+8, 4))
                    bitstream.append(boollist_to_int_var(val_list_2))
                else:
                    if current_pixel[3] == last_pixel[3]:
                        bitstream.append(254)
                        for c in (0,1,2):
                            bitstream.append(current_pixel[c])
                    else:
                        bitstream.append(255)
                        for c in (0,1,2,3):
                            bitstream.append(current_pixel[c])
                index_table[index_position] = current_pixel
                last_pixel = current_pixel
    if runcounter: # flush run
        bitstream.append(191+runcounter)
        runcounter = 0

    return bytes(header+bitstream+footer)

def decode(qoi: bytes):
    if not qoi[0:4] == b"qoif":
        raise ValueError("Not a QOI Image!")
    if len(qoi) < 15:
        raise ValueError("Invalid QOI Image!")
    width = int.from_bytes(qoi[4:8], "big")
    height = int.from_bytes(qoi[8:12], "big")
    channels = qoi[12]
    colorspace = qoi[13]
    listmap = blank_bitmap_list(width, height)
    seek = 14 # Start of QOI Data

    run_length = 0
    last_pixel = (0,0,0,255)

    index_table = [(0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)]
 # initialize to blank

    for y in range(height):
        for x in range(width):
            try:
                if seek >= len(qoi):
                    print("stream terminated prematurely!")
                    return listmap
                if run_length:
                    listmap[y][x] = last_pixel
                    run_length -= 1
                else:
                    byte_as_list = generate_boollist(qoi[seek], 8)

                    if qoi[seek] == 254: # QOI_OP_RGB
                        listmap[y][x] = (qoi[seek+1], qoi[seek+2], qoi[seek+3], last_pixel[3])
                        seek+=4
                    elif qoi[seek] == 255: # QOI_OP_RGBA
                        listmap[y][x] = (qoi[seek+1], qoi[seek+2], qoi[seek+3], qoi[seek+4])
                        seek+=5
                    elif byte_as_list[0:2] == [True, True]: # QOI_OP_RUN
                        run_length = boollist_to_int_var(byte_as_list[2:8]) # 1 pixel is already handled here
                        listmap[y][x] = last_pixel
                        seek+=1
                    elif byte_as_list[0:2] == [False, True]: # QOI_OP_DIFF
                        listmap[y][x] = [0,0,0,last_pixel[3]]
                        rd = last_pixel[0]+boollist_to_int_var(byte_as_list[2:4])-2
                        gd = last_pixel[1]+boollist_to_int_var(byte_as_list[4:6])-2
                        bd = last_pixel[2]+boollist_to_int_var(byte_as_list[6:8])-2
                        listmap[y][x][0] = intclamp(rd)
                        listmap[y][x][1] = intclamp(gd)
                        listmap[y][x][2] = intclamp(bd)
                        listmap[y][x] = tuple(listmap[y][x])
                        seek+=1
                    elif byte_as_list[0:2] == [True, False]: # QOI_OP_LUMA
                        listmap[y][x] = [0,0,0,last_pixel[3]]
                        byte2_as_list = generate_boollist(qoi[seek+1], 8)

                        rd = boollist_to_int_var(byte2_as_list[0:4])-8
                        gd = boollist_to_int_var(byte_as_list[2:8])-32
                        bd = boollist_to_int_var(byte2_as_list[4:8])-8

                        r = last_pixel[0] + gd + rd
                        g = last_pixel[1] + gd
                        b = last_pixel[2] + gd + bd

                        listmap[y][x][0] = intclamp(r)
                        listmap[y][x][1] = intclamp(g)
                        listmap[y][x][2] = intclamp(b)
                        listmap[y][x] = tuple(listmap[y][x])
                        seek+=2
                    elif byte_as_list[0:2] == [False, False]: # QOI_OP_INDEX
                        listmap[y][x] = index_table[boollist_to_int_var(byte_as_list[2:8])]
                        seek+=1
                    last_pixel = listmap[y][x]
                    if last_pixel is None:
                        last_pixel = (0,0,0,255)

                    index_position = (last_pixel[0] * 3 + last_pixel[1] * 5 + last_pixel[2] * 7 + last_pixel[3] * 11) % 64
                    index_table[index_position] = last_pixel
            except Exception:
                print("decoding error, failing! (likely premature stream termination)")
                return listmap
    return listmap