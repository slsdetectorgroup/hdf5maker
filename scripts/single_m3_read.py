import hdf5maker as h5m
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

from _hdf5maker import frame_header_dt

new_file = '/home/l_frojdh/data/ms3/run_I0_master_0.json'
# old_file = '/home/l_frojdh/software/hdf5maker/tests/data/TiScan_master_0.raw'

# fname = '/home/l_frojdh/data/ms/run_master_0.raw'

f = h5m.RawFile(new_file)

data = f.read()
# # plt.imshow(data[0])
# N = 10000
# i0 = np.zeros(N)
# with open('/home/l_frojdh/data/ms3/run_I0_d0_f0_0.raw', 'rb') as f:
#     for i in range(N):
#         h = np.fromfile(f, count = 1, dtype= frame_header_dt)
#         i0[i] = np.fromfile(f, count = 1280, dtype = np.uint8).sum()
        
#         print(f.tell(), i0[i].sum())
# plt.plot(i0)