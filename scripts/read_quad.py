import hdf5plugin
import h5py
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

import hdf5maker as h5m
# fq = False
# r1 = h5m.RawFile('/home/l_frojdh/data/epfl/run_master_0.raw', fastquad=fq, redistribute=False)
# data1 = r1.read()

# # fig, ax = plt.subplots()
# # im = ax.imshow(data[0])
# # im.set_clim(0,20000)

# r2 = h5m.RawFile('/home/l_frojdh/data/epfl/run_master_0.raw', fastquad=True, redistribute=True)
# data2 = r2.read()
# a = data1[0,:,0:514]
# b = data2[0]
# plt.imshow(a==b)

# np.save('tests/data/run_0.npy', data2)

from pathlib import Path
fpath = Path('/home/l_frojdh/data/epfl/2kHz/run_master_1.raw')

data = h5m.RawFile(fpath, fastquad=True).read()