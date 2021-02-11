
from hdf5maker.raw_master_file import *
from pathlib import Path

def test_parse_raw_fname():
    m = RawMasterFile('test_master_1.raw', lazy= True)
    m._parse_fname()
    assert m.run_id == 1
    assert m.base == Path('test')


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

    assert m['Total Frames'] == 1
    assert m['Dynamic Range'] == 32
    assert m['Quad'] == 0
    assert m['Pixels'] == (512, 256)

def test_read_mythen3_master_file():
    fpath = Path(__file__).parent / "data/TiScan_master_0.raw"
    m = RawMasterFile(fpath)


def test_eiger_master_file_data_file_names():
    fpath = Path(__file__).parent / "data/sample_master_2.raw"
    m = RawMasterFile(fpath)

    assert len(m.data_file_names) == 8
    assert m.data_file_names[0] == fpath.parent/'sample_d0_f0_2.raw'
    assert m.data_file_names[1] == fpath.parent/'sample_d1_f0_2.raw'
    assert m.data_file_names[2] == fpath.parent/'sample_d2_f0_2.raw'
    assert m.data_file_names[3] == fpath.parent/'sample_d3_f0_2.raw'