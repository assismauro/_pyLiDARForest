# -*- coding: utf-8 -*-
import os
import sys
import glob
import fnmatch
import laspy
import numpy as np
import subprocess
import shapefile
import shutil
import tempfile
import math

class idLASFile(object):

    def __init__(self, inputfname, parameters):
        self.inputfname = inputfname
        try:
            self.inFile = laspy.file.File(self.inputfname, mode = 'rw')
        except:
            print("Impossible to open file {0}".format(self.inputfname)

    def Execute():
        
