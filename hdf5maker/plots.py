
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from .formatting import color

def i0_graph(fname, data, i0):
    fname = Path(fname).with_suffix('.png')
    fig, ax = plt.subplots(1,2, figsize = (16,9))
    ax[0].plot(data.sum(axis = 0))
    ax[0].set_title('i0 sum')
    ax[0].set_xlabel('Channel [1]')

    ax[1].plot(i0)
    ax[1].set_title('i0')
    ax[1].set_xlabel('Frame [1]')

    for a in ax:
        a.grid()
    print(color.plotc(f"Saving: {fname}"))
    fig.savefig(fname)

def im_plot(fname, image):
    fname = Path(fname).with_suffix('.png')
    fig, ax = plt.subplots(1,1, figsize = (12,10))
    im = ax.imshow(image)
    plt.colorbar(im)
    set_clim(im)
    ax.set_title(fname.stem)
    print(color.plotc(f"Saving: {fname}"))
    fig.savefig(fname)


def set_clim(im, fraction=0.97, lower=0):
    arr = np.sort(im.get_array().data.flat)
    lim = arr[int(arr.size * fraction)]
    clim = lower, (1, lim)[lim>0]
    im.set_clim(clim)