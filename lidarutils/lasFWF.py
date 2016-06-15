# -*- coding: utf-8 -*-
import os
import fnmatch
import laspy
import numpy as np
import subprocess
import shapefile
import shutil
import tempfile
import math
import binascii
import struct

class FWFFile(laspy.file.File):
    def __init__(self, filename,
                   header=None,
                   vlrs=False,
                   mode='r',
                   in_srs=None,
                   out_srs=None,
                   evlrs = False):
        self.fwffilename=os.path.splitext(filename)[0]+'.wdp'
        self.fwffile=open(self.fwffilename, "rb")
        super(FWFFile,self).__init__(filename,header,vlrs,mode,in_srs,out_srs,evlrs)

    def GetFWFData(self,position,length):
        self.fwffile.seek(position)
        buff=self.fwffile.read(length)
        packed_data = binascii.unhexlify('0100000061620000cdcc2c40')
        values=hexlify(buff)
        x=struct.unpack(int,values)
        print x

