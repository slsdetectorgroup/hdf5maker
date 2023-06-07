import setuptools
from os.path import dirname, isdir, join
import os
import re
import subprocess
import sys
sys.path.append('hdf5maker')
from version import get_version

import numpy as np

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


c_ext = setuptools.Extension("_hdf5maker",
                  sources = ["src/raw_file.c", "src/hdf5maker.c"],
                  libraries = ['c',],
                  include_dirs=[np.get_include(),],
                  extra_compile_args = [],
                  )

setuptools.setup(
    name="hdf5maker",
    version= '2023.6.7.dev0',
    author="Erik Frojdh",
    author_email="erik.frojdh@psi.ch",
    description="Eiger raw file to hdf5 converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slsdetectorgroup/hdf5maker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL License",
        "Operating System :: OS Independent",
    ],
    ext_modules=[c_ext],
    python_requires='>=3.8',
)
