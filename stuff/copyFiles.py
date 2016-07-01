# -*- coding: utf-8 -*-
"""
Created on Wed Jun 15 14:07:07 2016

@author: Mauro Assis
"""
import os
import argparse
from argparse import RawTextHelpFormatter
import sys

import fnmatch
import time
import shutil

def FindFiles(directory, pattern):
     flist=[]
     for root, dirs, files in os.walk(directory):
         for filename in fnmatch.filter(files, pattern):
             flist.append(os.path.join(root, filename))
     return flist

fnames=sorted(FindFiles(r"H:\PASTAS_SBET_SUBSTITUIR","*.*"))
for fname in fnames:
    destination = r"h:\TRANSECTS\T_{0}\SBET_T-{0}_SHP\{1}".format(fname[-7:][0:3],os.path.basename(fname))
    print "Copy {0} to {1}:".format(fname,destination),"... ",
    shutil.copyfile(fname,destination)
    print "done."
