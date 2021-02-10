

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


def test_get_frames_to_read():
    # fname, frame_size, dr, frames_per_file, lazy = False
    reader = RawDataFile('dummy_d0_f0_0.raw', (256,512), 16, [], lazy = True)
    reader.frames_per_file = [5000, 5000, 5000]
    reader.current_frame = 4000
    reader.file_index = 0

    assert reader.get_frames_to_read(32) == [32]
    assert reader.get_frames_to_read(2000) == [1000, 1000]
    assert reader.get_frames_to_read(3000) == [1000, 2000]
    assert reader.get_frames_to_read(8000) == [1000, 5000, 2000]

    reader.file_index = 2
    reader.current_frame = 4000
    reader.frames_per_file = [1000, 2000, 3000, 6000]
    assert reader.get_frames_to_read(3000) == [2000, 1000]
    assert reader.get_frames_to_read(900) == [900]
    assert reader.get_frames_to_read(8000) == [2000, 6000]


    reader.frames_per_file = [5000, 5000, 5000, 5000]
    reader.current_frame = 9000
    reader.file_index = 1
    assert reader.get_frames_to_read(1) == [1]

