import hdf5plugin
import h5py
import fabio
import hdf5maker as h5m
from pathlib import Path
from argparse import ArgumentParser


def read_mask(fname):
    # read input data --> uint8 numpy array
    if fname is None:
        print("No input file to process")
        exit(1)
    elif fname.suffix == ".edf":
        print(f'Loading mask from edf file: {fname}')
        edf = fabio.edfimage.EdfImage().read(args.input)
        data = edf.data
    elif fname.suffix == ".h5":
        print(f"Extracting mask from Eiger data file ({fname})")
        f = h5py.File(args.input, 'r')
        data = f['entry/instrument/detector/detectorSpecific/pixel_mask'][:]
        f.close()
    else:
        raise ValueError(f"Unknown format of file: {args.input}")
    return data

def read_pixel_list(fname):
    """fname --> list, return empty list if fname is None"""
    if fname is not None:
        return h5m.read_bad_pixels(fname)
    else:
        return []


def write_mask(fname, data, header):
    outfile = fname.with_suffix('.edf')
    print(f'Writing mask to: {outfile}')
    fabio.edfimage.edfimage(header=header, data=data).write(outfile)

parser = ArgumentParser()
parser.add_argument(
    "-i",
    "--input",
    help="File with of bad pixels in row, col format",
    default=None,
    type=Path,
)
parser.add_argument(
    "-o",
    "--output",
    help="File with of bad pixels in row, col format",
    default=None,
    type=Path,
)
parser.add_argument(
    "-b",
    "--bad_pixels",
    help="File with of bad pixels in row, col format",
    default=None,
    type=Path,
)

args = parser.parse_args()


#Check arguments:
if args.output is None:
    raise ValueError("No output file specified")

data = read_mask(args.input)
pixels = read_pixel_list(args.bad_pixels)

print(f'Masking additional pixels from: {args.bad_pixels}')
for (row, col) in pixels:
    print(row, col)
    data[row, col] = 1


header = {'source_file': {args.input}, 'additional_pixels': args.bad_pixels}
write_mask(args.output, data, header)

