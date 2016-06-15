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

def FindFiles(directory, pattern):
     flist=[]
     for root, dirs, files in os.walk(directory):
         for filename in fnmatch.filter(files, pattern):
             flist.append(os.path.join(root, filename))
     return flist

fnames=FindFiles(r"H:\PASTAS_SBET_SUBSTITUIR","*.*")
print