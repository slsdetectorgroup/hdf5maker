
from .io import read_master_file, frame_header_dt, to_dtype
import numpy as np
from pathlib import Path
import os

def get_module_mask():
    module_mask = np.zeros((514,1030), dtype = np.bool)
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
        image[a] = np.ceil(top)
        image[a-1] = np.floor(top)
        image[b] = np.ceil(bottom)
        image[b+1] = np.floor(bottom)
        row-=514+36
    while col>0:
        for c in [256,514,772]:
            a = col-c
            b = col-(c+3)
            left = image[:,a]/2
            right = image[:,b]/2
            image[:,a] = np.ceil(left)
            image[:,a-1] = np.floor(left)
            image[:,b] =np.ceil(right)
            image[:,b+1] = np.floor(right)
        col-=1030
    return image


def read_frame_header(f):
    return np.fromfile(f, count=1, dtype = frame_header_dt)

def read_frame(f, dr):
    """
    Read a single frame from an open file
    """
    if dr in [8,16,32]:
        dt = np.dtype( 'uint{:d}'.format(dr) )
        return np.fromfile(f, dtype = dt, count = 256*512).reshape((256,512))
    elif dr == 4:
        dt = np.dtype('uint8')
        tmp = np.fromfile(f, dtype = dt, count = 256*256)
        data = np.zeros( tmp.size * 2, dtype = tmp.dtype )
        data[0::2] = np.bitwise_and(tmp, 0x0f)
        data[1::2] = np.bitwise_and(tmp >> 4, 0x0f)
        print('shape', data.shape)
        return data.reshape((256,512))
    else:
        raise ValueError(f"Unknown dynamic range: {dr}")


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

    modules = []
    for col in range(nmod[1]):
        y = image_size[0]
        for row in range(nmod[0]):
            rs = (y-514, y, 1)
            cs = (col*1030, (col+1)*1030, 1)
            modules.append((slice(*rs), slice(*cs)))
            y-=514+36

    return image_size, ports, modules

class RawDataFile:
    def __init__(self, fname, frame_size, dr, frames_per_file):
        self.dr = dr
        self._f = open(fname, 'rb')
        self.h0 = self.read_frame_header()
        self._f.seek(0, os.SEEK_SET)
        self.rows, self.cols = frame_size
        self.n_elements = self.rows*self.cols
        self.total_frames = sum(frames_per_file)
        self.current_frame = 0

        self.flip_rows = self.h0['Row'] % 2 == 1

    def read(self, n_frames = -1):
        #check if we can read 
        if n_frames == -1:
            n_frames = self.total_frames

        if n_frames > self.total_frames - self.current_frame:
            raise ValueError("Not enough frames left in file")

        header = np.zeros(n_frames, dtype = frame_header_dt)
        data = np.zeros((n_frames, self.rows, self.cols))

        for i in range(n_frames):
            header[i] = self.read_frame_header()
            data[i] = self.read_frame()
            self.current_frame += 1

        return header, data

        

    def read_frame_header(self):
        return np.fromfile(self._f, count=1, dtype = frame_header_dt)[0]

    def read_frame(self):
        """
        Read a single frame from an open file
        """
        #now we actually know the dr could optimize? 
        if self.dr in [8,16,32]:
            dt = np.dtype( 'uint{:d}'.format(self.dr) )
            data =  np.fromfile(self._f, dtype = dt, count = self.n_elements).reshape((self.rows,self.cols))
        elif self.dr == 4:
            dt = np.dtype('uint8')
            tmp = np.fromfile(self._f, dtype = dt, count = self.n_elements)
            data = np.zeros( tmp.size * 2, dtype = tmp.dtype )
            data[0::2] = np.bitwise_and(tmp, 0x0f)
            data[1::2] = np.bitwise_and(tmp >> 4, 0x0f)
            print('shape', data.shape)
            data.reshape((self.rows,self.cols))
        else:
            raise ValueError(f"Unknown dynamic range: {dr}")

        if self.flip_rows:
            data = data[::-1,:]
        return data


class EigerRawFileReader:
    module_mask = get_module_mask()

    def __init__(self, fname):
        fname = Path(fname)
        self.fname = fname
        self.master = read_master_file(self.fname)
        self.base, self.run_id = parse_raw_fname(self.fname)
        self.default_value = 0 #used for module gaps
        
        
        self.dt = to_dtype(self.master['Dynamic Range'])
        self.dr = self.master['Dynamic Range']
        self.total_frames = self.master['Total Frames']
        self.max_frames_per_file = self.master['Max Frames Per File']
        self.file_geometry = self.master['Pixels'][::-1]
        # self.n_files = -(-self.total_frames // self.max_frames_per_file) #-(-a // b)
        self.frames = get_frames_per_file(self.total_frames, self.max_frames_per_file)
        self._fid = 0
        
        #open the first files
        self._raw_file_names = [f'{self.base}_d{i}_f{self._fid}_{self.run_id}.raw' for i in range(self.master['nmod']*2)]
        self.files = [RawDataFile(f, self.file_geometry, self.dr, self.frames) for f in self._raw_file_names]
        self.find_geometry()

        self.image_size, self._ports, self._modules = calculate_size_and_slices(self._raw_pixels)
        
        self.mask = np.zeros(self.image_size, dtype=np.bool)
        for mod in self._modules:
            self.mask[mod] = self.module_mask

        self.module_gaps = np.ones(self.image_size, dtype=np.bool)
        for mod in self._modules:
            self.module_gaps[mod] = False



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

    def read(self, n_frames = -1):
        if n_frames == -1:
            n_frames = self.total_frames
        print(f"Reading: {n_frames} frames")
        image = np.zeros((n_frames, *self.image_size), dtype = self.dt)
        raw_image = np.zeros(self._raw_pixels, dtype = self.dt)
        for i in range(n_frames):
            for f,s in list(zip(self.files, self._ports)):
                h, raw_image[s] = f.read(1)

        
            image[i][self.mask] = raw_image.flat
            image[i] = split_counts(image[i])
            image[i][self.module_gaps] = self.default_value
        return image


def parse_raw_fname(fname):
    try:
        fname = Path(fname)
        base, _, run_id = fname.stem.rsplit('_', 2)
        base = fname.parent/base
        run_id = int(run_id)
    except:
        raise ValueError(f"Could not parse master file name: {fname}")

    return base, run_id

def get_frames_per_file(total_frames, frames_per_file):
    frames = [frames_per_file for i in range(total_frames//frames_per_file)]
    if total_frames % frames_per_file:
        frames.append(total_frames-frames_per_file*len(frames))
    return frames