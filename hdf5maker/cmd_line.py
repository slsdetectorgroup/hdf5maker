    
import argparse
from pathlib import Path
def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Master file of input data", type = Path)
    parser.add_argument("path_out", help="Output path for hdf5 files", type = Path)
    parser.add_argument("-j", "--num_threads", help="Number of threads used for processing", type = int, default=4)
    parser.add_argument("-n", "--custom_name", help="Custom name for the output file",  default=None)
    parser.add_argument("-b", "--bad_pixels", help="File with of bad pixels in row, col format",  default=None, type=Path)
    parser.add_argument("-s", "--sample", help="Only convert the first 100 frames", action="store_true")
    parser.add_argument("-g", "--graphs", help="Save graphs for fast feedback", action="store_true")
    return parser