# Package metadata lives in pyproject.toml. This file only describes the
# C extension, which the [project] table cannot express.
import numpy as np
import setuptools

c_ext = setuptools.Extension(
    "hdf5maker._hdf5maker",
    sources=["src/raw_file.c", "src/hdf5maker.c"],
    include_dirs=[np.get_include()],
    depends=["src/raw_file.h", "src/eiger_defs.h"],
)

setuptools.setup(ext_modules=[c_ext])
