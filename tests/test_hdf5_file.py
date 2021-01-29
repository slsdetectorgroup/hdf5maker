from hdf5maker import get_output_fname
from pathlib import Path

def test_get_output_fname():
    fname = '/some/path/to/file'
    out = get_output_fname(fname)
    assert isinstance(out, Path)
    assert out.suffix == '.h5'