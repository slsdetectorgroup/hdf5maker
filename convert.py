#!/usr/bin/env python 

import argparse
from pathlib import Path

from hdf5maker import get_output_fname, EigerRawFileReader

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Master file of input data", type = Path)
    parser.add_argument("output", help="Master file of output data", type = Path)
    args = parser.parse_args()

    fname_in = args.input
    fname_out = args.output
    #parsing

    print(f'Reading from: {fname_in}')
    print(f'Writing to: {fname_out}')

    raw_file = EigerRawFileReader(fname_in)

    # data = np.zeros(dtype = raw_file.dt)

    # hdf5_file = Hdf5FileWriter(fname_out)

    # for frame in raw_file:
    #     hdf5_file.write()