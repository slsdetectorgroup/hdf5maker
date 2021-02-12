from pathlib import Path
import numpy as np
import os

import _hdf5maker as _h5m
from _hdf5maker import frame_header_dt


class RawDataFile:
    def __init__(self, fname, frame_size, dr, frames_per_file, lazy = False, detector_type = 'Eiger'):
        self.dr = dr
        self.file_index = 0
        self.fname = Path(fname)
        self.base, _, self.end = self.fname.name.rsplit('_', 2)
        self.databytes =  np.prod(frame_size )* self.dr // 8
        self.total_frames = sum(frames_per_file)
        self.frames_per_file = np.array(frames_per_file)
        self._edge = np.cumsum(self.frames_per_file)
        self.current_frame = 0
        if not lazy:
            self._f = open(self.fname, 'rb')
            self.h0 = np.fromfile(self._f, count =1, dtype=frame_header_dt)[0]
            self._f.seek(0, os.SEEK_SET)

        if detector_type == 'Eiger':
            self._rf = _h5m.read_frame
        elif detector_type == 'Mythen3':
            self._rf = _h5m.read_m3
        else:
            raise ValueError(f"Unsupported detector type: {detector_type}")
        

    def _next_file_name(self):
        self.file_index += 1
        return self._file_name_from_index(self.file_index)

    def _file_name_from_index(self, file_index):
         return self.fname.parent/f'{self.base}_f{file_index}_{self.end}'

    def _file_index_from_frame_number(self, frame_number):
        for i, image_nr_high in enumerate(self._edge):
            if frame_number < image_nr_high:
                return i

    def open_next_file(self):
        self.open_file(self._next_file_name())

    def open_file(self, fname):
        self._f.close()
        self.fname = fname
        print(f"Opening: {self.fname}")
        self._f = open(self.fname, 'rb')

    def close(self):
        self._f.close()

    def seek(self, n_frames):
        #no need do check already done at top level? 
        frame_number = self.current_frame+n_frames
        i = self._file_index_from_frame_number(frame_number)
        if i != self.file_index:
            self.file_index = i
            self.open_file(self._file_name_from_index(i))
            if i>0:
                self.current_frame = self._edge[i-1]
            else: 
                self.current_frame = 0 #We opened the first file

        frames_to_seek = frame_number - self.current_frame
        n_bytes = (frame_header_dt.itemsize+self.databytes)*frames_to_seek
        if n_bytes != 0:
            self._f.seek(n_bytes)
            self.current_frame += frames_to_seek
    



    def read(self, n_frames = None, header = False):
        if n_frames is None:
            n_frames = self.total_frames

        data = []
        for i,n in enumerate(self.get_frames_to_read(n_frames)):
            if i!=0:
                self.open_next_file()
            data.append(self._rf(self._f, self.dr, n))

        self.current_frame += n_frames
        images = np.vstack(tuple(d[1] for d in data))    
        if header: 
            h = np.vstack(tuple(d[0] for d in data))   
            return h, images 
        else:
            return images
        
    def get_frames_to_read(self, n_frames):
        """
        Return a list of the number of frames to read per file
        """
        left_in_file = sum(self.frames_per_file[0:self.file_index+1])-self.current_frame
        frames_to_read = [(left_in_file, n_frames)[bool(n_frames<= left_in_file)]] #silence pytest warning
        frames_left_to_read = n_frames-sum(frames_to_read)
        if not frames_left_to_read:
            return frames_to_read

        for n in self.frames_per_file[self.file_index+1:]:
            if n > frames_left_to_read:
                frames_to_read.append(frames_left_to_read)
                break
            else:
                frames_to_read.append(n)
                frames_left_to_read -= n

        return frames_to_read