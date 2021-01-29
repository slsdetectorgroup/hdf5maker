import hdf5plugin
import h5py
from pathlib import Path
import numpy as np
# from sls_detector_tools.plot import imshow
# from sls_detector_tools.hdf5 import save



from hdfmaker import EigerRawFileReader

path = Path('/home/l_frojdh/tmp/1M/')
raw_file = EigerRawFileReader(path/'test', 1)
image = raw_file.read()
image = image.reshape(1,*image.shape)
mask = raw_file.module_gaps.copy()




def string_dt(s):
    tid = h5py.h5t.C_S1.copy()
    tid.set_size(len(s))
    return h5py.Datatype(tid)

def create_string_attr(obj, key, value):
    if value[-1] != '\x00':
        value += '\x00'
    print(f'{key=}, {value=}')
    obj.attrs.create(key, value, dtype = string_dt(value))
         
#Generate the individual files 
start = 1
stop = 6
base = 'hoi'

img_nr = 1
for i in range(start,stop,1):
    fpath = path/f'{base}_data_{i:06d}.h5'
    print(fpath)
    f = h5py.File(fpath, 'w')
    nxentry = f.create_group("entry")
    create_string_attr(nxentry, 'NX_class', 'NXentry')
    nxdata = nxentry.create_group("data")
    create_string_attr(nxdata, 'NX_class', 'NXdata')
    ds = nxdata.create_dataset("data", 
                                shape = (10,image.shape[1], image.shape[2]),
                                dtype = image.dtype,
                                maxshape = (None, image.shape[1], image.shape[2]),
                                # chunks = image.shape, 
                                **hdf5plugin.Bitshuffle(nelems=0, lz4=True))

    for j in range(10):
        ds[j] = np.zeros((1064,1030))+j

    ds.attrs["image_nr_low"] = np.int32(img_nr)
    ds.attrs["image_nr_high"] = np.int32(img_nr+9)
    img_nr+=10
    
    

    f.close()


#Generate master file
with h5py.File(path/f"{base}_master.h5", 'w') as f:
    nxentry = f.create_group("entry")
    create_string_attr(nxentry, 'NX_class', 'NXentry')
    nxdata = nxentry.create_group("data")
    create_string_attr(nxdata, 'NX_class', 'NXdata')
    for i in range(start, stop, 1):
        f[f'entry/data/data_{i:06d}'] = h5py.ExternalLink(f'{base}_data_{i:06d}.h5', 'entry/data/data')

    nxentry.create_group("instrument/data")
    inst = nxentry.create_group("instrument/detector/detectorSpecific")
    inst.create_dataset('pixel_mask', data = mask.astype(np.uint8), **hdf5plugin.Bitshuffle(nelems=0, lz4=True))

