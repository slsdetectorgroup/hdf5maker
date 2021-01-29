

from hdf5maker.raw_file import *
from pathlib import Path

def test_parse_raw_fname():
    base, run_id = parse_raw_fname('test_master_1.raw')
    assert run_id == 1
    assert base == Path('test')


def test_parse_raw_fname_with_path():
    base, run_id = parse_raw_fname('/path/to/some_file_master_32.raw')
    assert run_id == 32
    assert base == Path('/path/to/some_file')


def test_frames_per_file():
    total_frames = 5000
    frames_per_file = 1000
    assert get_frames_per_file(total_frames, frames_per_file) == [1000,1000,1000,1000,1000]

    frames_per_file = 3000
    assert get_frames_per_file(total_frames, frames_per_file) == [3000, 2000]