

from hdf5maker.raw_file_reader import *
from pathlib import Path


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


def test_get_next_file_name():
    reader = RawDataFile('dummy_d0_f0_0.raw', (256,512), 16, [], lazy = True)
    assert reader._next_file_name() == Path('dummy_d0_f1_0.raw')
    assert reader.file_index == 1
    assert reader._next_file_name() == Path('dummy_d0_f2_0.raw')
    assert reader.file_index == 2
    assert reader._next_file_name() == Path('dummy_d0_f3_0.raw')
    assert reader.file_index == 3
    assert reader._next_file_name() == Path('dummy_d0_f4_0.raw')
    assert reader.file_index == 4


def test_file_index_from_frame_number():
    reader = RawDataFile('dummy_d0_f0_0.raw', (256,512), 16, [5000,5000,5000,5000], lazy = True)
    assert reader._file_index_from_frame_number(0) == 0
    assert reader._file_index_from_frame_number(100) == 0
    assert reader._file_index_from_frame_number(4999) == 0
    assert reader._file_index_from_frame_number(5000) == 1
    assert reader._file_index_from_frame_number(16000) == 3