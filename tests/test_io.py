from pathlib import Path

from hdfmaker.io import read_master_file, _guess_geometry

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


def test_guess_geometry():
    assert _guess_geometry(2) == '500k'
    assert _guess_geometry(4) == '1M'


