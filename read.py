import numpy as np
from pathlib import Path
from sls_detector_tools.plot import imshow
import matplotlib.pyplot as plt
plt.ion()
from hdf5maker.raw_file import RawDataFile, EigerRawFileReader
from hdf5maker.hdf5_file import Hdf5FileWriter
import time
import hdf5plugin
import h5py

path = Path('/home/l_frojdh/tmp/1M/')
raw = EigerRawFileReader(path/'test1_master_0.raw')

size = (raw.dr//8*1024*1024)/1e6

# f = RawDataFile(path/'calibration_d6_f0_3.raw', raw.file_geometry, raw.master['Dynamic Range'], raw.frames)
N = 5000
t0 = time.time()
image = raw.read(N)
t = time.time()-t0
print(f'Reading {N} frames took {t:.2}s {size*N/t:.2f} MB/s')

ax, im = imshow(image[0])
im.set_clim(0,10)

#Now write this out to a hdf5 file 
t0 = time.time()
path_out = Path('/home/l_frojdh/tmp/1M/converted/')
h5f = Hdf5FileWriter(path_out/'test_master.h5')
h5f.write_data_file(path_out/'test_data_000001.h5', image, 1)
h5f.pixel_mask = raw.module_gaps
h5f.write_master_file()
t = time.time()-t0
print(f'Writing {N} frames took {t:.2}s {size*N/t:.2f} MB/s (uncompressed)')


#readback 
f = h5py.File(path_out/'test_master.h5', 'r')
data = f['entry/data/data_000001'][()]