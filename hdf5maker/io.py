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

def read_bad_pixels(fname):
    """
    Read ascii file with bad pixels in row, col format
    """

    pixels = []
    with open(fname, "r") as f:
        try:
            for line in f:
                if line[0] == "#":
                    continue
                row, col = line.split(",")
                pixels.append((int(row), int(col)))
        except:
            raise ValueError(f"Could not parse bad pixels file: {fname}")

    return pixels

def read_bad_channels(fname):
    channels = []
    with open(fname, "r") as f:
        try:
            for line in f:
                if line[0] == "#":
                    continue
                channels.append(int(line))
        except:
            raise ValueError(f"Could not parse bad channels file: {fname}")

    return channels