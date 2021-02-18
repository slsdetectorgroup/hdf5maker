

import re
import subprocess
from os.path import dirname, isdir, join
from pathlib import Path
import os
import pkg_resources

def version():
    try:
        return pkg_resources.require("hdf5maker")[0].version
    except:
        return get_version()

def get_version():
    version_re = re.compile('^Version: (.+)$', re.M)
    dev_re = re.compile('.dev\d+', re.M)

    path = Path(__file__).parent.as_posix()
    d = dirname(path)
    

    if isdir(join(d, '.git')):
        cmd = 'git describe --tags --match [0-9]*'.split()
        try:
            version = subprocess.check_output(cmd).decode().strip()
        except subprocess.CalledProcessError:
            print('Unable to get version number from git tags')
            exit(1)

        if '-' in version:
            version = version.split('-')[0]

        # Don't declare a version "dirty" merely because a time stamp has
        # changed. If it is dirty, append a ".dev1" suffix to indicate a
        # development revision after the release.
        with open(os.devnull, 'w') as fd_devnull:
            subprocess.call(['git', 'status'],
                            stdout=fd_devnull, stderr=fd_devnull)

        cmd = 'git diff-index --name-only HEAD'.split()
        try:
            dirty = subprocess.check_output(cmd).decode().strip()
        except subprocess.CalledProcessError:
            print('Unable to get git index status')
            exit(1)

        if dirty != '':
            r = dev_re.search(version)
            if r:
                version = version.replace(r.group(0), '')
            version += '.dev1'

    else:
        # Extract the version from the PKG-INFO file.
        with open(join(d, 'PKG-INFO')) as f:
            version = version_re.search(f.read()).group(1)

    return version