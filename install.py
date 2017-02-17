# This script downloads Mechanic and Ghostlines as .zip files into tmp, and then installs them into RoboFont.

import os
from urllib2 import urlopen
import zipfile as zf
from vanilla import dialogs

from mojo.extensions import *

temp = '/tmp/'

def unzip(zip_file_path, dest_dir):
    zipped_dir = zf.ZipFile(zip_file_path)
    for name in zipped_dir.namelist():
        (dir_name, file_name) = os.path.split(name)
        
        if file_name == '':
            # so this file is a directory
            new_dir = dest_dir + '/' + dir_name
            if not os.path.exists(new_dir):
                os.mkdir(new_dir)
        else:
            # so this is a file with an extension
            fd = open(dest_dir + '/' + name, 'wb')
            fd.write(zipped_dir.read(name))
            fd.close()

    zipped_dir.close()

def download(url, dest_dir):
    zip_path = temp + dest_dir + '.zip'
    response = urlopen(url)
    CHUNK = 16 * 1024
    with open(zip_path, 'wb') as f:
        while True:
            chunk = response.read(CHUNK)
            if not chunk:
                break
            f.write(chunk)

    unzip(zip_path, temp) # Unzip it into temp

def install_extension(url, dest_dir, ext_name):
    """Download extension, unzip it, and install in RoboFont."""

    download(url, dest_dir)
    extension_path = temp + dest_dir + '/' + ext_name
    extension = ExtensionBundle(extension_path)
    extension.install()

########## end functions, now the script ##########

install_extension('https://github.com/jackjennings/Mechanic/archive/master.zip', 'Mechanic-master', 'Mechanic.roboFontExt')
install_extension('https://github.com/ghostlines/ghostlines-robofont/archive/v1.zip', 'ghostlines-robofont-master', 'Ghostlines.roboFontExt')

try:
    import mechanic
except:
    dialogs.message("Error installing Mechanic.")

try:
    import ghostlines
except:
    dialogs.message("Error installing Ghostlines.")

from ghostlines.windows.account_window import AccountWindow
AccountWindow().open()
