from pathlib import Path
import numpy as np

frame_header_dt = [('Frame Number', 'u8'), 
                   ('SubFrame Number/ExpLength', 'u4'), 
                   ('Packet Number', 'u4'), 
                   ('Bunch ID', 'u8'),
                   ('Timestamp', 'u8'),
                   ('Module Id', 'u2'),
                   ('Row', 'u2'),
                   ('Column', 'u2'),
                   ('Reserved', 'u2'),
                   ('Debug', 'u4'),
                   ('Round Robin Number', 'u2'),
                   ('Detector Type', 'u1'),
                   ('Header Version', 'u1'),
                   ('Packets Caught Mask', 'V64'),
                   ]



def to_dtype(bits):
    if bits == 4:
        return np.uint8
    elif bits == 8:
        return np.uint8
    elif bits == 16:
        return np.uint16
    elif bits == 32:
        return np.uint32
    else:
        raise ValueError("unkown bit depth")

def _guess_geometry(nmod):
    if nmod == 2:
        return '500k'
    elif nmod == 4:
        return '1M'
    else:
        raise ValueError('Could not guess geometry')

def load_file(fname, n_frames, dr):
    header = np.zeros(n_frames, dtype=frame_header_dt)
    data = np.zeros((n_frames, 256, 512), dtype=to_dtype(dr))
    with open(fname, 'rb') as f:
        for i in range(n_frames):
            header[i] = read_frame_header(f)
            data[i] = read_frame(f, dr)

    return data, header


# def load_module(base):


def get_slice(row, col):
    return slice(None, None,None), slice(row*256, (row+1)*256, 1), slice(col*512, (col+1)*512, 1)


def load_raw(base, run_id, n_frames = -1, geometry = None, default = 0, shift = 0):

    #fname is the file name of the master file
    master_fname = f'{base}_master_{run_id}.raw'
    master = read_master_file(master_fname)

    # if geometry is None:
    #     geometry = _guess_geometry(master['nmod'])

    if n_frames == -1:
        n_frames = master["Total Frames"]

    

    #Read n_frames from each file
    fname_end =  f'_f0_{run_id}.raw' #TODO! Don't assume f0
    

    

    #data that is going to be returned 
    dt = to_dtype(master['Dynamic Range'])
    images = np.full((n_frames, 1024, 1024), default, dtype = dt)


    #0
    for i in range(master['nmod']*2):
        fname = f'{base}_d{shift+i}{fname_end}'
        print(f"Reading {n_frames} frames from {fname}")
        data, header = load_file(fname, n_frames, master['Dynamic Range'] )
        row,col = int(header['Row']), int(header['Column'])
        print(f'{fname} r:{row} c:{col}')   
        if row % 2:
            images[get_slice(row,col)] = data
        else:
            images[get_slice(row,col)] = data[:,::-1,:]


    # images = fix_large_pixels(images)
    return images, header, master  



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

def read_master_file(fname):
    """
    Read master file and return contents as a dict
    """
    master = {}
    with open(fname) as f:
        lines = f.readlines()

    it = iter(lines)

    for line in it:
        if line.startswith("#Frame"):
            break
        if line == "\n":
            continue
        field, value = line.split(":", 1)
        master[field.strip(" ")] = value.strip(" \n")

    frame_header = {}
    for line in it:
        field, value = line.split(":", 1)
        frame_header[field.strip()] = value.strip(" \n")

    master["Frame Header"] = frame_header
    return _parse_master_dict(master)


def _parse_master_dict(master):
    """
    Parse fields in the master file dict
    """

    for field in [
        "Max Frames Per File",
        "Frame Padding",
        "Total Frames",
        "Dynamic Range",
        "Ten Giga",
        "Quad",
        "Number of Lines read out",
    ]:
        master[field] = int(master[field])

    master['Rate Corrections'] = master['Rate Corrections'].strip('[]').split(',') 
    
    master['Pixels'] = tuple(int(i) for i in master['Pixels'].strip('[]').split(','))
    master['nmod'] = len(master['Rate Corrections'])
    return master


def fix_large_pixels(image, interpolation=True):
    #Check that rows and cols matches
    if image.shape[1] != 512 and image.shape[2] != 1024:
        raise ValueError('Unknown module size', image.shape)

    new_image = np.zeros((image.shape[0], 514, 1030), dtype=image.dtype)
    for i,img in enumerate(image):
        new_image[i] = _fix_large_pixels(img,interpolation=interpolation)

    return new_image

def _fix_large_pixels(image, interpolation=True):
    """
    Internal use to expand one frame for one module
    Give the option to interplate pixels or just copy values
    """
    new_image = np.zeros((514, 1030))

    new_image[0:256,    0:256] = image[  0:256,   0: 256]
    new_image[0:256,  258:514] = image[  0:256, 256: 512]
    new_image[0:256,  516:772] = image[  0:256, 512: 768]
    new_image[0:256, 774:1030] = image[  0:256, 768:1024]

    new_image[258:514,    0:256] = image[  256:512,   0: 256]
    new_image[258:514,  258:514] = image[  256:512, 256: 512]
    new_image[258:514,  516:772] = image[  256:512, 512: 768]
    new_image[258:514, 774:1030] = image[  256:512, 768:1024]


    #Interpolation
    if interpolation:
        new_image[255, :] /= 2
        new_image[258, :] /= 2
        d = (new_image[258, :]-new_image[255, :]) / 4
        new_image[256, :] = new_image[255, :] + d
        new_image[257, :] = new_image[258, :] - d


        new_image[:, 255] /= 2
        new_image[:, 258] /= 2
        d = (new_image[:, 258]-new_image[:, 255]) / 4
        new_image[:, 256] = new_image[:, 255] + d
        new_image[:, 257] = new_image[:, 258] - d

        new_image[:, 513] /= 2
        new_image[:, 516] /= 2
        d = (new_image[:, 516]-new_image[:, 513]) / 4
        new_image[:, 514] = new_image[:, 513] + d
        new_image[:, 515] = new_image[:, 516] - d

        new_image[:, 771] /= 2
        new_image[:, 774] /= 2
        d = (new_image[:, 774]-new_image[:, 771]) / 4
        new_image[:, 772] = new_image[:, 771] + d
        new_image[:, 773] = new_image[:, 774] - d


    return new_image