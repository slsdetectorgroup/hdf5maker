from pathlib import Path
from hdf5maker.hdf5_file import get_output_fname

def test_get_output_fname():
    path_out = '/some/path/to/'
    fname_in = '/another/path/to/a_file_name_master_8.raw'
    out = get_output_fname(fname_in, path_out)
    assert isinstance(out, Path)
    assert out == Path('/some/path/to/a_file_name_0008.h5')


def test_get_output_fname_custom_name():
    path_out = '/some/path/to/'
    fname_in = '/another/path/to/a_file_name_master_19.raw'
    out = get_output_fname(fname_in, path_out, 'special')
    assert isinstance(out, Path)
    assert out == Path('/some/path/to/special_0019.h5')