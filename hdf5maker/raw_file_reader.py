from .io import to_dtype
from .raw_data_file import RawDataFile
from .raw_master_file import RawMasterFile
from .formatting import color
from .tools import find_suffix
import numpy as np
from pathlib import Path
import os

import _hdf5maker as _h5m

frame_header_dt = _h5m.frame_header_dt


def get_module_mask(image_size = (514,1030)):
    """
    Returns a mask that selects real pixels from an image that 
    also contains extra gap pixels. Assumes that the module
    size is 514, 1030 unless specified smaller.
    """
    #TODO! Deal with large Mythen3
    if len(image_size)==1:
        return np.ones((image_size), dtype=np.bool_)

    image_size = np.min(((514,1030),image_size), axis = 0)
    module_mask = np.zeros((image_size), dtype=np.bool_)
    module_mask[0:256, 0:256] = True
    module_mask[0:256, 258:514] = True
    module_mask[258:514, 0:256] = True
    module_mask[258:514, 258:514] = True

    if np.all(image_size == (514,1030)):
        module_mask[0:256, 516:772] = True
        module_mask[0:256, 774:1030] = True
        module_mask[258:514, 516:772] = True
        module_mask[258:514, 774:1030] = True
    return module_mask


def split_counts(image):
    """
    Splits counts on full image. 
    """
    row, col = image.shape
    while row > 0:
        a = row - 256
        b = a - 3
        top = image[a] / 2
        bottom = image[b] / 2
        r = np.random.randint(0, 2, top.size)
        image[a] = top + r * 0.5
        image[a - 1] = top + (1 - r) * 0.5
        r = np.random.randint(0, 2, bottom.size)
        image[b] = bottom + r * 0.5
        image[b + 1] = bottom + (1 - r) * 0.5
        row -= 514 + 36
    while col > 0:
        for c in [256, 514, 772]:
            a = col - c
            b = col - (c + 3)
            if b<0:
                break
            left = image[:, a] / 2
            right = image[:, b] / 2
            r = np.random.randint(0, 2, left.size)
            image[:, a] = left + r * 0.5
            image[:, a - 1] = left + (1 - r) * 0.5
            r = np.random.randint(0, 2, right.size)
            image[:, b] = right + r * 0.5
            image[:, b + 1] = right + (1 - r) * 0.5
        col -= 1030
    return image


def calculate_size_and_slices(geo):
    dt = np.int32
    raw_image_size = np.array(geo, dtype=dt)

    # Constishstans
    raw_module_size = np.array((512, 1024), dtype=dt)
    module_with_gappixels = np.array((514, 1030), dtype=dt)
    module_gaps = np.array((36, 0), dtype=dt)
    unit_size = np.array((256, 512), dtype=dt)

    if np.all(raw_image_size == (512,512)):
        raw_module_size = np.array((512, 512), dtype=dt)
        module_with_gappixels = np.array((514, 514), dtype=dt)

    # TODO add assertions
    nmod = raw_image_size // raw_module_size
    

    # TODO add assertions
    image_size = nmod * module_with_gappixels + module_gaps * (nmod - 1)

    nunit = raw_image_size // unit_size

    # Loop over ports/files
    ports = []
    for col in range(0, nunit[1], 2):
        y = raw_image_size[0]
        for r in range(nunit[0]):
            x = 512 * col
            for c in range(col, col + 2, 1):
                rs = (y - 256, y, 1)
                cs = (x, x + 512, 1)
                x += 512
                ports.append((slice(*rs), slice(*cs)))
            y -= 256

    port_wgap = []
    row_counter = 0
    for col in range(0, nunit[1], 2):
        y = image_size[0]
        for r in range(nunit[0]):
            x = 515 * col
            for c in range(col, col + 2, 1):
                rs = (y - 257, y, 1)
                cs = (x, x + 515, 1)
                x += 515
                port_wgap.append((slice(None, None, None), slice(*rs), slice(*cs)))
            y -= 257
            row_counter += 1
            if row_counter == 2:
                y -= 36
                row_counter = 0

    modules = []
    for col in range(nmod[1]):
        y = image_size[0]
        for row in range(nmod[0]):
            rs = (y - 514, y, 1)
            cs = (col * 1030, (col + 1) * 1030, 1)
            modules.append((slice(*rs), slice(*cs)))
            y -= 514 + 36

    #override things in case of fastquad
    if np.all(image_size == (514,514)):
    #     ports = [(slice(None, None, None),slice(0,256,1),slice(0,512,1)),(slice(None,None,None),slice(256,514,1), slice(0,512,1))]
        port_wgap =[(slice(None,None,None),slice(257,514,1), slice(0,514,1)), (slice(None, None, None),slice(0,257,1),slice(0,514,1))]
    return image_size, ports, port_wgap, modules



class RawFile:
    def __init__(self, fname, redistribute=None, lazy=False, fastquad=False):
        fname = Path(fname)

        #Deal with both old and new suffix
        fname = find_suffix(fname)
        if not fname.exists():
            raise IOError("Could not find raw master file: {fname}")
        self.fname = fname
        self.redistribute = redistribute
        self.default_value = 0  # used for module gaps
        self.current_frame = 0
        self.fastquad = fastquad

        if not lazy:
            self.master = RawMasterFile(self.fname, fastquad=fastquad)
            if self.redistribute is None:
                if self.master['Detector Type'] == 'Mythen3':
                    self.redistribute = False
                else:
                    self.redistribute = True
            self.dt = to_dtype(self.master["Dynamic Range"])
            self.dr = self.master["Dynamic Range"]
            self.total_frames = self.master["Total Frames"]
            self.max_frames_per_file = self.master["Max Frames Per File"]
            self.file_geometry = self.master["Pixels"][::-1]
            self.frames_per_file = get_frames_per_file(
                self.total_frames, self.max_frames_per_file
            )
            self._fid = 0


  

            # open the first files
            self.files = [
                RawDataFile(
                    f,
                    self.file_geometry,
                    self.dr,
                    self.frames_per_file,
                    detector_type=self.master["Detector Type"],
                )
                for f in self.master.data_file_names
            ]
            self.find_geometry()

            

            if self.master["Detector Type"] == "Mythen3":
                self.image_size = self._raw_pixels[1:2]
                self._ports = None
                self._pwg = [(slice(None, None,None), s) for s in self._slices]
                self._modules = []
            else:
                (
                    self.image_size,
                    self._ports,
                    self._pwg,
                    self._modules,
                ) = calculate_size_and_slices(self._raw_pixels)


            self.module_mask = get_module_mask(self.image_size)
            self.mask = np.zeros(self.image_size, dtype=np.bool_)
            for mod in self._modules:
                self.mask[mod] = self.module_mask

            self.module_gaps = np.ones(self.image_size, dtype=np.bool_)
            for mod in self._modules:
                self.module_gaps[mod] = False

    def seek(self, n_frames):
        frames_left = self.total_frames - self.current_frame
        if n_frames > frames_left:
            raise ValueError(
                f"Cannot advance {n_frames} with only {frames_left} frames left"
            )

        for f in self.files:
            f.seek(n_frames)

        self.current_frame += n_frames

    def close(self):
        for f in self.files:
            f.close()

    def find_geometry(self):
        """
        Figure out geometry by reading the first header from each
        raw file combined with info from the master file
        """
        row = []
        col = []
        self._slices = []
        x, y = self.master["Pixels"]

        if self.master["Detector Type"] == "Mythen3":
            for f in self.files:
                r, c = f.h0["Row"], f.h0["Column"]
                row.append(r)
                col.append(c)
                self._slices.append(slice(c * x, (c + 1) * x, 1))  # assume only col
        else:
            for f in self.files:
                r, c = f.h0["Row"], f.h0["Column"]
                row.append(r)
                col.append(c)
                self._slices.append(
                    (slice(r * y, (r + 1) * y, 1), slice(c * x, (c + 1) * x, 1))
                )

        # Some assertion that all files are there?
        self._raw_pixels = (
            np.array((max(row) + 1, max(col) + 1)) * self.master["Pixels"][::-1]
        )
        return self._raw_pixels

    def read(self, n_frames=None):
        if n_frames is None:
            n_frames = self.total_frames
        print(f"Reading: {n_frames} frames")
        image = np.zeros((n_frames, *self.image_size), dtype=self.dt)

        for f, s in list(zip(self.files, self._pwg)):
            if self.fastquad:
                image[s] = f.read(n_frames)[:,:,0:514]
            else:
                image[s] = f.read(n_frames)
        self.current_frame += n_frames

        if self.redistribute:
            for frame in image:
                split_counts(frame)
        return image


def get_frames_per_file(total_frames, frames_per_file):
    frames = [frames_per_file for i in range(total_frames // frames_per_file)]
    if total_frames % frames_per_file:
        frames.append(total_frames - frames_per_file * len(frames))
    return frames
