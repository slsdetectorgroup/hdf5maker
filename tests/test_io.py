from pathlib import Path
from hdf5maker.io import read_bad_pixels


def test_read_bad_pixels():
    fname = Path(__file__).parent / "data/bad_pixels.txt"
    pixels = read_bad_pixels(fname)

    assert pixels == [(597, 496), (300, 200)]



