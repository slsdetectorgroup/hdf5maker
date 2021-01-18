
from .io import read_master_file, frame_header_dt

class RawFileReader:

    def __init__(self, fname, run_id):
        self.fname = f'{fname}_master_{run_id}.raw'
        self.master = read_master_file(self.fname)


    def find_geometry(self):
        """
        Figure out geometry by reading the first header from each
        raw file combined with info from the master file
        """