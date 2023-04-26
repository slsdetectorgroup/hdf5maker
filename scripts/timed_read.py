import h5py
import hdf5plugin
import time

t0 = time.time()
f = h5py.File('/home/l_frojdh/tmp/1M/conv/new_0000.h5', 'r')

# data = [ds[()] for key, ds in f['entry/data'].items()]
ds = f['entry/data/data_000001']
print(ds.shape)
print(time.time()-t0)