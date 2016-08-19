import os
import subprocess
import shutil 

lidarutilspath = "e:\\CCST\\Software\\LiDAR-Python-Code\\pre_processing\\"
lastoolspath = "C:\\LAStools\\bin\\"
fusionpath = "c:\\fusion\\"

def FindFiles(directory, pattern):
    flist=[]
    for root, dirs, files in os.walk(directory):
        for filename in fnmatch.filter(files, pattern):
            flist.append(os.path.join(root, filename))
    return flist

def run_command(command,verbose=False):
     p = subprocess.Popen(command,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
     return p.communicate()
     


