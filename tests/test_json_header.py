import pytest
from pathlib import Path
from hdf5maker import RawMasterFile
import numpy as np


def test_load_master():
    fpath = Path(__file__).parent / "data/m3_master_0.json"
    m = RawMasterFile(fpath)

    assert m.json == True

    assert m['Version'] == 7.1
    #timestamp
    assert m['Detector Type'] == 'Mythen3'
    assert m['Timing Mode'] == 'auto'
    assert m['Geometry']['x'] == 1
    assert m['Geometry']['y'] == 1
    assert m['Image Size in bytes'] == 15360
    
    #added to be compatible with old files
    assert m['Image Size'] == 15360 

    #should in principle have 'x' and 'y' but stays col, row to be compatible
    #TODO! refactor so that old also uses the new syntac
    assert m['Pixels'] == (3840, 1)
    assert m['Max Frames Per File'] == 10000
    assert m['Frame Discard Policy'] == 'nodiscard'
    assert m['Frame Padding'] == 1
    assert m['Scan Parameters'] == "[disabled]"
    assert m['Total Frames'] == 1
    assert m['Dynamic Range'] == 32
    assert m['Ten Giga'] == 1

    assert m['Period'] == np.timedelta64(2000000, 'ns')

    assert m['Exptime1'] == np.timedelta64(100000000, 'ns')
    assert m['Exptime2'] == np.timedelta64(100000000, 'ns')
    assert m['Exptime3'] == np.timedelta64(100000000, 'ns')

    assert m['GateDelay1'] == np.timedelta64(0, 'ns')
    assert m['GateDelay2'] == np.timedelta64(0, 'ns')
    assert m['GateDelay3'] == np.timedelta64(0, 'ns')

    assert m['Gates'] == 1
    assert m['Threshold Energies'] == [-1, -1, -1]

    assert m['Frames in File'] == 1

    assert m['nmod'] == 1