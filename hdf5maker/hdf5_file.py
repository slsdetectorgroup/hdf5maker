from pathlib import Path
import hdf5plugin
import h5py
import numpy as np

from .raw_master_file import RawMasterFile
from .formatting import color

def string_dt(s):
    tid = h5py.h5t.C_S1.copy()
    tid.set_size(len(s))
    return h5py.Datatype(tid)

def create_string_attr(obj, key, value):
    #Albula requires null terminated strings
    if value[-1] != "\x00":
        value += "\x00"
    obj.attrs.create(key, value, dtype=string_dt(value))

def create_entry_and_data(hdf5_file):
    nxentry = hdf5_file.create_group("entry")
    create_string_attr(nxentry, "NX_class", "NXentry")
    nxdata = nxentry.create_group("data")
    create_string_attr(nxdata, "NX_class", "NXdata")
    return nxentry, nxdata

def write_data_file(
    fname,
    data,
    image_nr_low=1,
    compression=hdf5plugin.Bitshuffle(nelems=0, lz4=True),
):
    print(color.info(f"Writing: {fname}"))
    f = h5py.File(fname, "w")
    nxentry, nxdata = create_entry_and_data(f)
    ds = nxdata.create_dataset(
        "data",
        data=data,
        shape=data.shape,
        dtype=data.dtype,
        maxshape=(None, *data.shape[1:]),
        chunks = (1, data.shape[1], data.shape[2]),
        **compression,
    )
    ds.attrs["image_nr_low"] = np.int32(image_nr_low)
    ds.attrs["image_nr_high"] = np.int32(image_nr_low + data.shape[0] - 1)
    f.close()


def write_master_file(
    fname,
    data_files,
    pixel_mask=None,
    i0 = None,
    compression=hdf5plugin.Bitshuffle(nelems=0, lz4=True),
):
    print(color.info(f"Writing: {fname}"))
    f = h5py.File(fname, "w")
    nxentry, nxdata = create_entry_and_data(f)

    # Link written data sets:
    for i, fname in enumerate(data_files, start=1):
        f[f"entry/data/data_{i:06d}"] = h5py.ExternalLink(fname, "entry/data/data")

    #Group to hold instrument specific data
    grp = nxentry.create_group("instrument/data")

    # Pixel mask recognized by Albula
    if pixel_mask is not None:
        inst = nxentry.create_group("instrument/detector/detectorSpecific")
        inst.create_dataset("pixel_mask", data=pixel_mask.astype(np.uint8), **compression)

    if i0 is not None:
        grp.create_dataset("i0", data=i0, **compression)
    f.close()


def get_output_fname(fname_in, path_out, fname_out = None):
    fname_in = Path(fname_in)
    path_out = Path(path_out)
    m = RawMasterFile(fname_in, lazy=True)
    m._parse_fname()
    if fname_out is None:
        fname_out = m.base.name

    return path_out/f'{fname_out}_{m.run_id:04d}.h5'
    