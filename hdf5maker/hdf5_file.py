from pathlib import Path
import hdf5plugin
import h5py
import numpy as np

from .raw_master_file import RawMasterFile
from .formatting import color

class Hdf5File:
    """
    Interface to read hdf5 file written by hdf5maker should also accept
    Dectris files
    """
    def __init__(self, fname, options = 'r'):
        self._f = h5py.File(fname, options)
        self._data_sets = [ds for ds in self._f['entry/data'].values()]
        
        edge = [ds.shape[0] for ds in self._data_sets]
        self._last_frame = np.cumsum(edge)
        self.n_frames = sum(edge)
        self.n_datasets = len(self._data_sets)


    def __getitem__(self, frame_number):
        #TODO! Reuse code from RawFile
        if frame_number < self.n_frames:
            dataset_index = np.argmax(self._last_frame > frame_number)
            local_frame_index = frame_number - (self._last_frame[dataset_index]-self._data_sets[dataset_index].shape[0])
            print(f'{dataset_index=}, {local_frame_index=}')
            return self._data_sets[dataset_index][local_frame_index]
        else:
            raise ValueError("Requested frame number exceeds number of frames in file")

    def __iter__(self):
        for data_set in self._data_sets:
            for frame in data_set:
                yield frame

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
        chunks = (1, *data.shape[1:]),
        **compression,
    )
    ds.attrs["image_nr_low"] = np.int32(image_nr_low)
    ds.attrs["image_nr_high"] = np.int32(image_nr_low + data.shape[0] - 1)
    f.close()


def write_master_file(
    fname,
    data_files,
    pixel_mask=None,
    raw_master_file = None,
    i0 = None,
    compression=hdf5plugin.Bitshuffle(nelems=0, lz4=True),
):
    print(color.info(f"Writing: {fname}"))
    f = h5py.File(fname, "w")
    nxentry, nxdata = create_entry_and_data(f)



    if raw_master_file is not None:
        #add attrs
        fields = {'exptime': 'Exptime', 
                  'exptime1': 'Exptime1',
                  'exptime2': 'Exptime2', 
                  'exptime3': 'Exptime3', 
                  'period': 'Period', 
                 }

        # Copy times from the raw master file
        for attr,key in fields.items():
            if key in raw_master_file.dict:
                 nxdata.attrs[attr] = raw_master_file.dict[key].item()

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

    return path_out/f'{fname_out}_master_{m.run_id:04d}.h5'
    