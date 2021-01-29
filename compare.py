
import numpy as np
from pathlib import Path
path = Path('/home/l_frojdh/tmp/1M')
file1 = path/'export_data_000001.h5'
file2 = path/'hoi_data_000001.h5'


N = 10000
with open(file1, 'rb') as f:
    data1 = f.read(N)


with open(file2, 'rb') as f:
    data2 = f.read(N)


for i,(a,b) in enumerate(zip(data1,data2)):
    if a!=b:
        print(i,a,b)