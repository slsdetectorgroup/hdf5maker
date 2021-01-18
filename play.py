from hdfmaker.io import *
from pathlib import Path
import numpy as np
from sls_detector_tools.plot import imshow
import cbf

import matplotlib.pyplot as plt
plt.ion()
# # master = read_master_file('tests/data/sample_master.raw')
path = Path('/home/l_frojdh/data/1M')
# data, header, master = load_raw(path/'calibration',3, shift=0)
# # data, header, master = load_raw('/home/l_frojdh/data/quad/run',3)

# # arr = np.zeros(4, dtype= frame_header_dt)

# with open(path/'calibration_d3_f0_2.raw') as f:
#     h = read_frame_header(f)


# from sls_detector_tools.io import load_frame
# data = load_frame('/home/l_frojdh/data/quad/run',3)
# img = data[0]

# fig, ax = plt.subplots(figsize = (16,10))
# im = ax.imshow(img)
# im.set_clim(0,1e4)
# im.set_clim(0,5)

# c = cbf.read("/home/l_frojdh/data/1M/calibration_00003_00001.cbf")
# ax, im = imshow(c.data)
# im.set_clim(0,1e4)


from hdfmaker import RawFileReader

f = RawFileReader(path/'calibration', 2)
