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

def Header():
    print("Move files v0.8")
    print("")
    print("Processing...")

def ParseCmdLine():
    try:
        parser = argparse.ArgumentParser(description="Move files v0.8.",formatter_class=RawTextHelpFormatter)
        parser.add_argument("sourcedir",help="Source directory.")
        parser.add_argument("destinationdir",help="Destination directory.")
        parser.add_argument("-m","--filemasks", type=str ,help="File masks to be moved.") 
        parser.add_argument("-v","--verbose", type=int, help="show processing messages.", default = False)
        return parser.parse_args()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

if __name__ == "__main__":
    Header()
    args=ParseCmdLine()
    masks=args.filemasks.split(',')
    for mask in masks:
        fnames=sorted(FindFiles(args.sourcedir,mask))
        for fname in fnames:
            fnamedest=args.destinationdir+os.path.basename(fname)
            if fname != fnamedest:
                shutil.move(fname, fnamedest)
                if args.verbose == 1:
                    print("File {0} moved to {1}.").format(fname,fnamedest)
    print("Done.")
