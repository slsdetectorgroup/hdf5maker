
from hdf5maker.raw_master_file import *
from pathlib import Path
import numpy as np
import pytest

def test_parse_raw_fname():
    m = RawMasterFile('test_master_1.raw', lazy= True)
    m._parse_fname()
    assert m.run_id == 1
    assert m.base == Path('test')

def test_parse_raw_fname_with_multiple_underscores():
    m = RawMasterFile('some_file_that_is_master_876.raw', lazy= True)
    m._parse_fname()
    assert m.run_id == 876
    assert m.base == Path('some_file_that_is')

def test_parse_fname_without_index_throws():
    m = RawMasterFile('file_master).raw', lazy= True)
    with pytest.raises(ValueError):
        m._parse_fname()


def test_generate_data_fname():
    m = RawMasterFile('somename_master_7.raw', lazy= True)
    m._parse_fname()
    assert m.run_id == 7
    assert m.base == Path('somename')
    assert m.data_fname(0) == Path('somename_d0_f0_7.raw')
    assert m.data_fname(3) == Path('somename_d3_f0_7.raw')
    assert m.data_fname(37) == Path('somename_d37_f0_7.raw')


def test_parse_raw_fname_with_path():
    m = RawMasterFile('/path/to/some_file_master_32.raw', lazy = True)
    m._parse_fname()
    assert m.run_id == 32
    assert m.base == Path('/path/to/some_file')


def test_read_eiger_master_file():
    fpath = Path(__file__).parent / "data/sample_master_2.raw"
    m = RawMasterFile(fpath)

    assert m['Version'] == '6.2'

    assert m['Detector Type'] == 'Eiger'
    assert m['Timing Mode'] == 'auto'
    assert m['Image Size'] == 524288
    assert m['Pixels'] == (512, 256)
    assert m['Max Frames Per File'] == 5000
    assert m['Frame Discard Policy'] == 'nodiscard'
    assert m['Frame Padding'] == 1
    assert m['Scan Parameters'] == '[disabled]'
    assert m['Total Frames'] == 1
    assert m['Dynamic Range'] == 32
    assert m['Ten Giga'] == 1

    assert m['Exptime'] == np.timedelta64(int(10e9), 'ns')
    assert m['Period'] == np.timedelta64(int(1e9), 'ns')
    assert m['SubExptime'] == np.timedelta64(int(2.62144*1000*1000), 'ns')
    assert m['SubPeriod'] == np.timedelta64(int(2.62144*1000*1000), 'ns')
    assert m['Quad'] == 0
    assert m['Number of Lines read out'] == 256

    assert m['nmod'] == 4

def test_read_mythen3_master_file():
    fpath = Path(__file__).parent / "data/TiScan_master_0.raw"
    m = RawMasterFile(fpath)

    assert m['Version'] == '6.2'

    assert m['Detector Type'] == 'Mythen3'
    assert m['Timing Mode'] == 'trigger'
    assert m['Image Size'] == 5120
    assert m['Pixels'] == (1280, 1)
    assert m['Max Frames Per File'] == 10000
    assert m['Frame Discard Policy'] == 'nodiscard'
    assert m['Frame Padding'] == 1
    # assert m['Scan Parameters'] == '701'
    assert m['Total Frames'] == 701
    assert m['Dynamic Range'] == 32
    assert m['Ten Giga'] == 0

    assert m['Exptime1'] == np.timedelta64(100000000, 'ns')
    assert m['Exptime2'] == np.timedelta64(100000000, 'ns')
    assert m['Exptime3'] == np.timedelta64(100000000, 'ns')

    assert m['nmod'] == 2


def test_eiger_master_file_data_file_names():
    fpath = Path(__file__).parent / "data/sample_master_2.raw"
    m = RawMasterFile(fpath)

    assert len(m.data_file_names) == 8
    assert m.data_file_names[0] == fpath.parent/'sample_d0_f0_2.raw'
    assert m.data_file_names[1] == fpath.parent/'sample_d1_f0_2.raw'
    assert m.data_file_names[2] == fpath.parent/'sample_d2_f0_2.raw'
    assert m.data_file_names[3] == fpath.parent/'sample_d3_f0_2.raw'

def test_mythen3_master_file_data_file_names():
    fpath = Path(__file__).parent / "data/TiScan_master_0.raw"
    m = RawMasterFile(fpath)

    assert len(m.data_file_names) == 2
    assert m.data_file_names[0] == fpath.parent/'TiScan_d0_f0_0.raw'
    assert m.data_file_names[1] == fpath.parent/'TiScan_d1_f0_0.raw'

def test_parse_jungfrau_master_file():
    fpath = Path(__file__).parent / "data/run_master_16.raw"
    m = RawMasterFile(fpath)
    assert m['Detector Type'] == 'Jungfrau'
    assert m["Timing Mode"] == "auto"
    assert m['Image Size'] == 1048576
    assert m['Pixels'] == (1024, 512)
    assert m['Max Frames Per File'] == 10000
    assert m['Frame Discard Policy'] == 'nodiscard'
    assert m['Frame Padding'] == 1
    assert m['Scan Parameters'] == '[disabled]'
    assert m['Total Frames'] == 10
    assert m['Exptime'] == np.timedelta64(500, 'us')
    assert m['Period'] == 0
    assert m['Number of UDP Interfaces'] == 1


def test_parse_exptime():
    assert RawMasterFile.to_nanoseconds('10s') == np.timedelta64(int(10e9), 'ns')
    assert RawMasterFile.to_nanoseconds('10ns') == np.timedelta64(10, 'ns')
    assert RawMasterFile.to_nanoseconds('3ms') == np.timedelta64(3 * 1000*1000, 'ns')
    assert RawMasterFile.to_nanoseconds('2.62144ms').item() == 2.62144*1000*1000