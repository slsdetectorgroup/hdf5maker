from .io import to_dtype
from .raw_data_file import RawDataFile
from .raw_master_file import RawMasterFile
import numpy as np
from pathlib import Path
import os

import _hdf5maker as _h5m
frame_header_dt = _h5m.frame_header_dt

def get_module_mask():
    """
    Selects real pixels from module with gap pixels
    """
    module_mask = np.zeros((514,1030), dtype = np.bool_)
    module_mask[0:256,    0:256] = True
    module_mask[0:256,  258:514] = True
    module_mask[0:256,  516:772] = True
    module_mask[0:256, 774:1030] = True

    module_mask[258:514,    0:256] = True
    module_mask[258:514,  258:514] = True
    module_mask[258:514,  516:772] = True
    module_mask[258:514, 774:1030] = True
    return module_mask


def split_counts(image):
    row, col = image.shape
    while row>0:
        a = row-256
        b = a-3
        top = image[a]/2
        bottom = image[b]/2
        r = np.random.randint(0, 2, top.size)
        image[a] = top + r *.5
        image[a-1] = top + (1-r) * .5
        r = np.random.randint(0, 2, bottom.size)
        image[b] = bottom + r * .5
        image[b+1] = bottom + (1-r) * .5
        row-=514+36
    while col>0:
        for c in [256,514,772]:
            a = col-c
            b = col-(c+3)
            left = image[:,a]/2
            right = image[:,b]/2
            r = np.random.randint(0, 2, left.size)
            image[:,a] = left + r * .5
            image[:,a-1] = left + (1-r) * .5
            r = np.random.randint(0, 2, right.size)
            image[:,b] =right + r * .5
            image[:,b+1] = right + (1-r) * .5
        col-=1030
    return image

def calculate_size_and_slices(geo):
    dt = np.int
    raw_image_size = np.array(geo, dtype = dt)

    #Constants
    raw_module_size = np.array((512,1024), dtype = dt)
    module_with_gappixels = np.array((514, 1030), dtype = dt)
    module_gaps = np.array((36,0), dtype=dt)
    unit_size = np.array((256,512), dtype=dt)

    #TODO add assertions
    nmod =  raw_image_size//raw_module_size

    #TODO add assertions
    image_size = nmod*module_with_gappixels+module_gaps*(nmod-1)

    nunit = raw_image_size//unit_size

    #Loop over ports/files
    ports = []
    for col in range(0,nunit[1],2):
        y = raw_image_size[0]
        for r in range(nunit[0]):
            x = 512*col
            for c in range(col, col+2, 1):
                rs = (y-256, y, 1)
                cs = (x,x+512,1)
                x += 512
                ports.append((slice(*rs), slice(*cs)))
            y-=256

    port_wgap = []
    row_counter = 0
    for col in range(0,nunit[1],2):
        y = image_size[0]
        for r in range(nunit[0]):
            x = 515*col
            for c in range(col, col+2, 1):
                rs = (y-257, y, 1)
                cs = (x,x+515,1)
                x += 515
                port_wgap.append((slice(None, None, None), slice(*rs), slice(*cs)))
            y-=257
            row_counter += 1
            if row_counter == 2:
                y -= 36
                row_counter = 0

    modules = []
    for col in range(nmod[1]):
        y = image_size[0]
        for row in range(nmod[0]):
            rs = (y-514, y, 1)
            cs = (col*1030, (col+1)*1030, 1)
            modules.append((slice(*rs), slice(*cs)))
            y-=514+36

    return image_size, ports, port_wgap, modules




class EigerRawFileReader:
    module_mask = get_module_mask()

    def __init__(self, fname,  redistribute = True, lazy = False):
        fname = Path(fname)
        self.fname = fname
        self.redistribute = redistribute
        # self.base, self.run_id = parse_raw_fname(self.fname)
        self.default_value = 0 #used for module gaps
        self.current_frame = 0

        if not lazy:
            self.master = RawMasterFile(self.fname)
            self.dt = to_dtype(self.master['Dynamic Range'])
            self.dr = self.master['Dynamic Range']
            self.total_frames = self.master['Total Frames']
            self.max_frames_per_file = self.master['Max Frames Per File']
            self.file_geometry = self.master['Pixels'][::-1]
            self.frames_per_file = get_frames_per_file(self.total_frames, self.max_frames_per_file)
            self._fid = 0
        
            #open the first files
            # self._raw_file_names = [f'{self.base}_d{i}_f{self._fid}_{self.run_id}.raw' for i in range(self.master['nmod']*2)]
            self.files = [RawDataFile(f, self.file_geometry, self.dr, self.frames_per_file) for f in self.master.data_file_names]
            self.find_geometry()

            self.image_size, self._ports, self._pwg, self._modules = calculate_size_and_slices(self._raw_pixels)
        
            self.mask = np.zeros(self.image_size, dtype=np.bool_)
            for mod in self._modules:
                self.mask[mod] = self.module_mask

            self.module_gaps = np.ones(self.image_size, dtype=np.bool_)
            for mod in self._modules:
                self.module_gaps[mod] = False

    def seek(self, n_frames):
        frames_left = self.total_frames-self.current_frame
        if n_frames > frames_left:
            raise ValueError(f"Cannot advance {n_frames} with only {frames_left} frames left")

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
        x,y = self.master['Pixels']

        for f in self.files:
            # h = np.fromfile(fname, count = 1, dtype = frame_header_dt)[0]
            r,c = f.h0['Row'], f.h0['Column']
            row.append(r)
            col.append(c)
            self._slices.append((slice(r*y,(r+1)*y, 1), slice(c*x, (c+1)*x, 1)))

        #Some assertion that all files are there? 
        self._raw_pixels = np.array((max(row)+1, max(col)+1)) * self.master['Pixels'][::-1]
        return self._raw_pixels

    def _python_read(self, n_frames = -1):
        if n_frames == -1:
            n_frames = self.total_frames
        print(f"Reading: {n_frames} frames")
        image = np.zeros((n_frames, *self.image_size), dtype = self.dt)
        raw_image = np.zeros(self._raw_pixels, dtype = self.dt)
        for i in range(n_frames):
            for f,s in list(zip(self.files, self._ports)):
                h, raw_image[s] = f._python_read(1)

        
            image[i][self.mask] = raw_image.flat
            if self.redistribute:
                image[i] = split_counts(image[i])
            image[i][self.module_gaps] = self.default_value
        self.current_frame += n_frames
        return image

    def read(self, n_frames = None):
        if n_frames is None:
            n_frames = self.total_frames
        print(f"Reading: {n_frames} frames")
        image = np.zeros((n_frames, *self.image_size), dtype = self.dt)
        for f,s in list(zip(self.files, self._pwg)):
            image[s] = f.read(n_frames)
        self.current_frame += n_frames

        if self.redistribute:
            for frame in image:
                split_counts(frame)
        return image
    



def get_frames_per_file(total_frames, frames_per_file):
    frames = [frames_per_file for i in range(total_frames//frames_per_file)]
    if total_frames % frames_per_file:
        frames.append(total_frames-frames_per_file*len(frames))
    return frames


