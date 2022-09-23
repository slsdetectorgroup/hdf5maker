import pytest
from pathlib import Path
from hdf5maker.tools import find_suffix

def test_finds_json_file():
    #The file exists and has a json extension
    fpath = Path(__file__).parent / "data/m3_master_0"
    r = find_suffix(fpath)
    assert r == fpath.with_suffix('.json')

def test_finds_raw_file():
    #The file exists and has a raw extension
    fpath = Path(__file__).parent / "data/run_master_16"
    r = find_suffix(fpath)
    assert r == fpath.with_suffix('.raw')


def test_other_suffix():
    #When called with another suffix we just return it
    fpath = Path('/some/file.strange')
    r = find_suffix(fpath)
    assert r == fpath

def test_file_not_found():
    #if the file is not found we don't add anything
    fpath = Path('/path/to/some/file_asovknaslvna')
    r = find_suffix(fpath)
    assert r == fpath