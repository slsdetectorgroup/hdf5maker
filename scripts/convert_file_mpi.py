from mpi4py import MPI
from mpi4py.futures import MPIPoolExecutor
import argparse
import hdf5plugin
import h5py
import numpy as np
import time


def convert_data_file(fname_in, fname_out, start, stop):
    """
    Wrapper to read one data file and convert to hdf5
    """
    t0 = time.time()
    raw = h5m.RawFile(fname_in)
    raw.seek(start)
    data = raw.read(stop-start)
    t1 = time.time()
    h5m.write_data_file(fname_out, data, image_nr_low=start+1)
    t2 = time.time()
    return {'reading':t1-t0, 'writing':t2-t1}

def func(t, i):
    print(f"{i}: start")
    time.sleep(t)
    print(f"{i}: done")
    return i

if __name__ == "__main__":
    executor = MPIPoolExecutor(max_workers=3)
    iterable = ((2, n) for n in range(3))
    # for result in executor.starmap(func, iterable):
    #     print(result)

    result = [i for i in executor.starmap(func, iterable)]
