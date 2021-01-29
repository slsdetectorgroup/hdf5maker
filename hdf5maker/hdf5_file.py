from pathlib import Path
import hdf5plugin
import h5py
import numpy as np

class Hdf5FileWriter:
    def __init__(self, fname, compress = True):
        self.fname = fname
        self.data_files = []
        self._pixel_mask = None
        if compress:
            self._kwopts = hdf5plugin.Bitshuffle(nelems=0, lz4=True)
        else:
            self._kwopts = {}
        pass

    @property
    def pixel_mask(self):
        return self._pixel_mask

    @pixel_mask.setter
    def pixel_mask(self, pm):
        self._pixel_mask = pm.astype(np.uint8)

    def write_data_file(self, fname, data, image_nr_low):
        print(f'Writing: {fname}')
        f = h5py.File(fname, 'w')
        nxentry = f.create_group("entry")
        create_string_attr(nxentry, 'NX_class', 'NXentry')
        nxdata = nxentry.create_group("data")
        create_string_attr(nxdata, 'NX_class', 'NXdata')
        ds = nxdata.create_dataset("data", 
                                    data = data,
                                    shape = data.shape,
                                    dtype = data.dtype,
                                    maxshape = (None, *data.shape[1:]),
                                    # chunks = image.shape, 
                                    **self._kwopts)

        ds.attrs["image_nr_low"] = np.int32(image_nr_low)
        ds.attrs["image_nr_high"] = np.int32(image_nr_low+data.shape[0]-1)
        f.close()
        self.data_files.append(fname.name)

    def write_master_file(self):
        f = h5py.File(self.fname, 'w')
        nxentry = f.create_group("entry")
        create_string_attr(nxentry, 'NX_class', 'NXentry')
        nxdata = nxentry.create_group("data")
        create_string_attr(nxdata, 'NX_class', 'NXdata')

        #Loop over written data sets:
        for i, fname in enumerate(self.data_files, start=1):
            f[f'entry/data/data_{i:06d}'] = h5py.ExternalLink(fname, 'entry/data/data')


        if self._pixel_mask is not None:
            nxentry.create_group("instrument/data")
            inst = nxentry.create_group("instrument/detector/detectorSpecific")
            inst.create_dataset('pixel_mask', data = self._pixel_mask, **self._kwopts)
        f.close()


def string_dt(s):
    tid = h5py.h5t.C_S1.copy()
    tid.set_size(len(s))
    return h5py.Datatype(tid)

def create_string_attr(obj, key, value):
    if value[-1] != '\x00':
        value += '\x00'
    obj.attrs.create(key, value, dtype = string_dt(value))


def get_output_fname(fname, fname_in = None):
    fname = Path(fname)

    # if fname is None and fname_in is not None:
    #     #generate the output filename from the input filename
    #     base, run_id = parse_raw_fname(fname_in)

    # elif fname is not None and 




    if not fname.suffix:
        fname = fname.with_suffix('.h5')

    return fname