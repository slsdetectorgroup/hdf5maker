# hdfmaker

Python package to convert PSI Eiger raw files to hdf5 with Bitshuffle+LZ4. 


## Command line tool

```bash
#Usage
raw2hdf5 /path/to/run_master_0.raw /output/path/

raw2hdf5 -h #show usage

```

## Python API

*WIP*

## Data processing


## Limitations 

The software assumes that files are written with padding in the receiver such that each frame is header+data and no size variation due to packet loss. 

### Image size

The tool reads raw files from disk and uses row, col information in the frame header in combination with the master fileto figure out the image size.  

### Gap pixels

* Inter module gaps are by default set to 0, and marked as true in the pixel mask. 

* Large pixels on the chip borders are split in two (or four) with the counts split between pixels. In the case of an odd number of counts the extra count is randomly assigned to on of the pixels. 

### File format

* Nexus like hdf5 with Bitshuffle + LZ4
* Readable with Albula 4.x

**Master file**

The master holds in addition to the pixel mask only links to the data files 

```
HDF5 "test1_0000.h5" {
FILE_CONTENTS {
 group      /
 group      /entry
 group      /entry/data
 ext link   /entry/data/data_000001 -> test/test1_0000_000000.h5 entry/data/data
 group      /entry/instrument
 group      /entry/instrument/data
 group      /entry/instrument/detector
 group      /entry/instrument/detector/detectorSpecific
 dataset    /entry/instrument/detector/detectorSpecific/pixel_mask
 }
}
```

**Data file**

```
HDF5 "test1_0000_000000.h5" {
FILE_CONTENTS {
 group      /
 group      /entry
 group      /entry/data
 dataset    /entry/data/data
 }
}

```

## Dependencies

## Compatibility

We aim to follow NEP 29 regarding supported Python and Numpy versions https://numpy.org/neps/nep-0029-deprecation_policy.html#nep29

At the moment this means:
* Python 3.9-3.11
* Numpy 1.22-1.24
