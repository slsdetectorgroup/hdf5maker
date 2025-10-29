

from hdf5maker.raw_file_reader import *
from pathlib import Path
import pytest

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


def test_read_one_eiger_frame():
    fpath = Path(__file__).parent / "data/sample_master_2.raw"
    reader = RawFile(fpath)
    image = reader.read()
    assert image.shape == (1,1064, 1030)
    assert image.dtype == np.uint32

    #Compare normal pixels of image with the np gold standard image
    gold_standard = np.load(Path(__file__).parent / "data/sample_2.npy")
    mask = np.load(Path(__file__).parent / "data/mask.npy")
    assert image.sum() == gold_standard.sum()
    pm = np.broadcast_to(mask[np.newaxis,:,:], image.shape)
    assert np.all(image[pm] == gold_standard[pm])

def test_read_one_mythen3_file():
    fpath = Path(__file__).parent / "data/TiScan_master_0.raw"
    r = RawFile(fpath)
    data = r.read()
    assert data.shape == (701,2560)
    assert data.dtype == np.uint32

def test_read_one_mythen3_file_json():
    fpath = Path(__file__).parent / "data/m3_master_0.json"
    r = RawFile(fpath)
    data = r.read()
    assert data.shape == (1,3840)
    assert data.dtype == np.uint32

def test_read_one_mythen3_file_no_suffix():
    fpath = Path(__file__).parent / "data/TiScan_master_0"
    r = RawFile(fpath)
    data = r.read()
    assert data.shape == (701,2560)
    assert data.dtype == np.uint32

def test_read_directly_from_data_file():
    fpath = Path(__file__).parent / "data/TiScan_master_0.raw"
    r = RawFile(fpath)
    header, data = r.files[0].read(header=True)
    assert data.shape == (701,1280)
    assert np.all(np.diff(header['Frame Number'])==1)

def test_deal_with_empty_file():
    fpath = Path(__file__).parent / "data/empty_master_0.raw"
    with pytest.raises(IOError):
        r = RawFile(fpath)

def test_compare_fastquad_and_module():
    fpath = Path(__file__).parent / "data/run_master_0.raw"
    data1 = RawFile(fpath, redistribute=False).read()
    assert data1.shape == (1,514,1030)

    data2 = RawFile(fpath, redistribute=False, fastquad=True).read()
    assert data2.shape == (1,514,514)

    #When we don't redistribute data should be exactly the same
    assert np.all(data1[:,:,0:514] == data2)


def test_read_one_mythen3_file_with_new_header():
    fpath = Path(__file__).parent / "data/m3_master_0.json"
    f = RawFile(fpath)
    data = f.read()
    assert data.shape == (1,3840)
    assert data[0,0] == 0
    assert data[0,1] == 1

def test_read_one_mythen3_file_with_new_header_no_suffix():
    fpath = Path(__file__).parent / "data/m3_master_0"
    f = RawFile(fpath)
    data = f.read()
    assert data.shape == (1,3840)
    assert data[0,0] == 0
    assert data[0,1] == 1

def test_read_fastquad():
    fpath = Path(__file__).parent / "data/run_master_0.raw"
    image = RawFile(fpath, fastquad=True).read()
    assert image.shape == (1,514,514)
    
    #Check for regression
    gold_standard = np.load(Path(__file__).parent / "data/run_0.npy")
    mask = np.load(Path(__file__).parent / "data/mask.npy")[0:514,0:514]
    pm = np.broadcast_to(mask[np.newaxis,:,:], image.shape)
    assert np.all(image[pm] == gold_standard[pm])

def test_read_Eiger1M_v7():
    fpath = Path(__file__).parent / "data/EigerV7_master_0.json"
    image = RawFile(fpath).read()
    assert image.shape == (1,1064, 1030)
    gold_standard = np.load(Path(__file__).parent / "data/EigerV7_master_0.npy")
    mask = np.load(Path(__file__).parent / "data/mask.npy")
    pm = np.broadcast_to(mask[np.newaxis,:,:], image.shape)
    assert np.all(image[pm] == gold_standard[pm])
