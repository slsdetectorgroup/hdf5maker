import hdf5plugin
import h5py
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
plt.ion()

mask = np.load('mask.npy')


path = Path('/home/l_frojdh/tmp/')
f_old = h5py.File(path/'Ti64Cr_In10_6mm_L1_BM_00000_000000000000.h5', 'r')
data_old = f_old['entry/data/data'][()]

f_new = h5py.File(path/'Ti64Cr_In10_6mm_L1_BM_0000_000000.h5', 'r')
data_new = f_new['entry/data/data'][()]


pm = np.broadcast_to(mask[np.newaxis,:,:], data_old.shape)

# equal = np.all(data_new[pm]==data_old[pm])
# print(f'All normal pixels are the same: {equal}')

image_old = data_old.sum(axis = 0).astype(float)
image_new = data_new.sum(axis = 0).astype(float)
fig, ax = plt.subplots(1,3, figsize = (30,10))
im_old = ax[0].imshow(image_old)
im_new = ax[1].imshow(image_new)
im_diff = ax[2].imshow(image_old-image_new)

for im in [im_old, im_new]:
    im.set_clim(0,300)
im_diff.set_clim(-30,30)

ax[0].set_title("Old")
ax[1].set_title("New")
ax[2].set_title("Diff")

fig.savefig('comparison')
lim = (175,350)
for a in ax:
    a.set_xlim(lim)
    a.set_ylim(lim)

fig.savefig('comparison_zoom')