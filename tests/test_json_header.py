import pytest
from pathlib import Path
from hdf5maker import RawMasterFile
import numpy as np


def test_load_master():
    fpath = Path(__file__).parent / "data/m3_master_0.json"
    m = RawMasterFile(fpath)

    assert m['Version'] == 7.1

    assert m['Detector Type'] == 'Mythen3'
    assert m['Timing Mode'] == 'auto'
    assert m['Image Size'] == 15360
    assert m['Pixels'] == (3840, 1)
    assert m['Max Frames Per File'] == 10000
    assert m['Frame Discard Policy'] == 'nodiscard'
    assert m['Frame Padding'] == 1
    # assert m['Scan Parameters'] == '701'
    assert m['Total Frames'] == 1
    assert m['Dynamic Range'] == 32
    assert m['Ten Giga'] == 1

    assert m['Exptime1'] == np.timedelta64(100000000, 'ns')
    assert m['Exptime2'] == np.timedelta64(100000000, 'ns')
    assert m['Exptime3'] == np.timedelta64(100000000, 'ns')

    assert m['nmod'] == 1