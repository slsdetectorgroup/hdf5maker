import setuptools
from os.path import dirname, isdir, join
import os
import re
import subprocess
import sys
sys.path.append('hdf5maker')
from version import get_version
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# version_re = re.compile('^Version: (.+)$', re.M)
# dev_re = re.compile('.dev\d+', re.M)


# def get_version():
#     d = dirname(__file__)

#     if isdir(join(d, '.git')):
#         cmd = 'git describe --tags --match [0-9]*'.split()
#         try:
#             version = subprocess.check_output(cmd).decode().strip()
#         except subprocess.CalledProcessError:
#             print('Unable to get version number from git tags')
#             exit(1)

#         if '-' in version:
#             version = version.split('-')[0]

#         # Don't declare a version "dirty" merely because a time stamp has
#         # changed. If it is dirty, append a ".dev1" suffix to indicate a
#         # development revision after the release.
#         with open(os.devnull, 'w') as fd_devnull:
#             subprocess.call(['git', 'status'],
#                             stdout=fd_devnull, stderr=fd_devnull)

#         cmd = 'git diff-index --name-only HEAD'.split()
#         try:
#             dirty = subprocess.check_output(cmd).decode().strip()
#         except subprocess.CalledProcessError:
#             print('Unable to get git index status')
#             exit(1)

#         if dirty != '':
#             r = dev_re.search(version)
#             if r:
#                 version = version.replace(r.group(0), '')
#             version += '.dev1'

#     else:
#         # Extract the version from the PKG-INFO file.
#         with open(join(d, 'PKG-INFO')) as f:
#             version = version_re.search(f.read()).group(1)

#     return version

c_ext = setuptools.Extension("_hdf5maker",
                  sources = ["src/raw_file.c", "src/hdf5maker.c"],
                  libraries = ['c',],
                #   include_dirs=[np.get_include(),],
                  extra_compile_args = [],
                  )

setuptools.setup(
    name="hdf5maker",
    version= get_version(),
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