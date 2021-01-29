from pathlib import Path
import hdf5plugin
import h5py
import numpy as np

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
    print(f"Writing: {fname}")
    f = h5py.File(fname, "w")
    nxentry, nxdata = create_entry_and_data(f)
    ds = nxdata.create_dataset(
        "data",
        data=data,
        shape=data.shape,
        dtype=data.dtype,
        maxshape=(None, *data.shape[1:]),
        # chunks = image.shape,
        **compression,
    )

    ds.attrs["image_nr_low"] = np.int32(image_nr_low)
    ds.attrs["image_nr_high"] = np.int32(image_nr_low + data.shape[0] - 1)
    f.close()


def write_master_file(
    fname,
    data_files,
    pixel_mask=None,
    compression=hdf5plugin.Bitshuffle(nelems=0, lz4=True),
):
    f = h5py.File(fname, "w")
    nxentry, nxdata = create_entry_and_data(f)

    # Link written data sets:
    for i, fname in enumerate(data_files, start=1):
        f[f"entry/data/data_{i:06d}"] = h5py.ExternalLink(fname, "entry/data/data")

    # Pixel mask recognized by Albula
    if pixel_mask is not None:
        nxentry.create_group("instrument/data")
        inst = nxentry.create_group("instrument/detector/detectorSpecific")
        inst.create_dataset("pixel_mask", data=pixel_mask.astype(np.uint8), **compression)
    f.close()
