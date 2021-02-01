from pathlib import Path
import numpy as np


def to_dtype(bits):
    if bits == 4:
        return np.uint8
    elif bits == 8:
        return np.uint8
    elif bits == 16:
        return np.uint16
    elif bits == 32:
        return np.uint32
    else:
        raise ValueError("unkown bit depth")


def read_master_file(fname):
    """
    Read master file and return contents as a dict
    """
    master = {}
    with open(fname) as f:
        lines = f.readlines()

    it = iter(lines)

    for line in it:
        if line.startswith("#Frame"):
            break
        if line == "\n":
            continue
        field, value = line.split(":", 1)
        master[field.strip(" ")] = value.strip(" \n")

    frame_header = {}
    for line in it:
        field, value = line.split(":", 1)
        frame_header[field.strip()] = value.strip(" \n")

    master["Frame Header"] = frame_header
    return _parse_master_dict(master)


def _parse_master_dict(master):
    """
    Parse fields in the master file dict
    """

    for field in [
        "Max Frames Per File",
        "Frame Padding",
        "Total Frames",
        "Dynamic Range",
        "Ten Giga",
        "Quad",
        "Number of Lines read out",
    ]:
        master[field] = int(master[field])

    master['Rate Corrections'] = master['Rate Corrections'].strip('[]').split(',') 
    master['Pixels'] = tuple(int(i) for i in master['Pixels'].strip('[]').split(','))
    master['nmod'] = len(master['Rate Corrections'])
    return master


def read_bad_pixels(fname):
    """
    Read ascii file with bad pixels in row, col format
    """

    pixels = []
    with open(fname, 'r') as f:
        try:
            for line in f:
                if line[0] == '#':
                    continue
                row, col = line.split(',')
                pixels.append((int(row), int(col)))
        except:
            raise ValueError(f"Could not parse bad pixels file: {fname}")

    return pixels

    