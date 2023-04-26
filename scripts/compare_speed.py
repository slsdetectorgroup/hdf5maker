import hdf5maker as h5m
import hdf5plugin
import h5py
import time 
from pathlib import Path
import numpy as np
path_out = Path('/home/l_frojdh/tmp/1M/comp/')

# fname = Path('/home/l_frojdh/tmp/1M/test1_master_0.raw')
# r = h5m.RawFile(fname)
# data = r.read(5000)
# np.save(path_out/'data', data)

data = np.load(path_out/'data.npy')

with h5py.File(path_out/'comp.h5', 'r') as f:
    t0 = time.time()
    data = f['entry/data/data'][()]
    t1 = time.time()
    print(f'With compression read {data.shape} in {t1-t0:.2f}s')



data = np.load(path_out/'data.npy')

with h5py.File(path_out/'no_comp.h5', 'r') as f:
    t0 = time.time()
    data = f['entry/data/data'][()]
    t1 = time.time()
    print(f'Without compression read {data.shape} in {t1-t0:.2f}s')


# t0 = time.time()
# h5m.write_data_file(path_out/'comp.h5', data)
# t1 = time.time()
# h5m.write_data_file(path_out/'no_comp.h5', data, compression= {})
# t2 = time.time()
# print(f'Writing to disk took: {t1-t0:.2f} vs {t2-t1:.2f}s')

