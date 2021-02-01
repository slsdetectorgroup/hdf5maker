from pathlib import Path
from hdf5maker.io import read_master_file, read_bad_pixels


def test_read_master_file():
    fpath = Path(__file__).parent / "data/sample_master_2.raw"
    master = read_master_file(fpath)
    assert master['Version'] == '6.2'

    assert master['Detector Type'] == 'Eiger'
    assert master['Timing Mode'] == 'auto'

    assert master['Total Frames'] == 1
    assert master['Dynamic Range'] == 32
    assert master['Quad'] == 0
    assert master['Pixels'] == (512, 256)


def test_read_bad_pixels():
    fname = Path(__file__).parent / "data/bad_pixels.txt"
    pixels = read_bad_pixels(fname)

    assert pixels == [(597, 496), (300, 200)]



