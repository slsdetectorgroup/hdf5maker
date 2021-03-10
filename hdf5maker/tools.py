

from .formatting import color
from .raw_master_file import RawMasterFile
from pathlib import Path

def replace_total_frames(fname):
    fname = Path(fname)

    #Read current number of frames from file
    master = RawMasterFile(fname)
    current = master['Total Frames']
    size = master['Image Size'] + 112

    with open(fname, 'r') as f:
        lines = f.readlines()

    #Get number of frames form file size
    nframes = 0
    i = 0
    while True:
        data_file = master.data_fname(0, findex=i)
        if not data_file.exists():
            break
        
        if data_file.stat().st_size%size != 0:
            raise ValueError("Partial frames in file")
        nframes += data_file.stat().st_size//size
        i += 1

    #Replace line in list
    for i, line in enumerate(lines):
        if line.startswith('Total Frames'):
            start, _ = line.split(':')
            replacement = ':'.join((start, f' {nframes}\n'))
            lines[i] = replacement

    if current != nframes:
        print(color.yellow(f"Rewriting number of frames from: {current} to {nframes}"))

        #Write out content
        with open(fname, 'w') as f:
            f.writelines(lines)
    else:
        print(color.ok("Number of frames matches leaving the file alone"))