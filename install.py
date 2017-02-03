# This script downloads Mechanic and Ghostlines as .zip files into tmp, and then installs them into RoboFont.

from urllib2 import urlopen
import zipfile as zf
from mojo.extensions import *
from vanilla import dialogs
import os

temp = '/tmp/'

def unzip(zipFilePath, destDir):
    zipped_dir = zf.ZipFile(zipFilePath)
    for name in zipped_dir.namelist():
        (dirName, fileName) = os.path.split(name)
        if fileName == '':
            # so this file is a directory
            newDir = destDir + '/' + dirName
            if not os.path.exists(newDir):
                os.mkdir(newDir)
        else:
            # so this is a file with an extension
            fd = open(destDir + '/' + name, 'wb')
            fd.write(zipped_dir.read(name))
            fd.close()
    zipped_dir.close()

def download(url, destDir):
    zip_path = temp + destDir + '.zip'
    response = urlopen(url)
    CHUNK = 16 * 1024
    with open(zip_path, 'wb') as f:
        while True:
            chunk = response.read(CHUNK)
            if not chunk:
                break
            f.write(chunk)

    unzip(zip_path, temp) # Unzip it into temp

def install_extension(url, destDir, extName):
    """Download extension, unzip it, and install in RoboFont."""

    download(url,destDir)
    extension_path = temp + destDir + '/' + extName
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
AccountWindow.open()
