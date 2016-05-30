# -*- coding: utf-8 -*-
import os
import argparse
from argparse import RawTextHelpFormatter
import sys

import fnmatch
import time
from multiprocessing import Pool, Process

from valParameters import valParameters
from Validate import Validate
        
def Header():
    print("Find invalid values v0.8")
    print

def ParseCmdLine():
    parser = argparse.ArgumentParser(description="Find invalid values.",formatter_class=RawTextHelpFormatter)
    parser.add_argument("inputfname",help="las file to be processed.")
    parser.add_argument("-t","--tcoefficientvalues", help="Find X(t), Y(t), Z(t) inconsistent coefficient values.", default = None)
    return parser.parse_args()

if __name__ == "__main__":
    Header()
    args=ParseCmdLine()
