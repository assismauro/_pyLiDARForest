# -*- coding: utf-8 -*-
import sys
import os
import cv2
import numpy as np
from matplotlib import pyplot as plt
import argparse
import laspy
import pandas as pd

class las2img(object):

    def __init__(self, inputfname, verbose):
        self.inputfname = inputfname
        try:
            self.inFile = laspy.file.File(self.inputfname, mode = 'r')
            self.verbose=verbose
        except:
            print("Impossible to open file {0}".format(self.inputfname))

    @staticmethod
    def Header():
        print("LiDAR to Image v0.8")
        print("")
        print("Processing...")

    @staticmethod
    def ProcessCmdLine():
        # D:\CCST\Software\img2lidar\img\ebablog.png -x 807000 -y 9710000 -zf (z>0) -xr 0.5 -yr 0.5 -zr 0.20 -mz 100 -bz 100 -bxy 1 -d 5
        parser = argparse.ArgumentParser(description="Convert LiDAR (las) to image file.")
        parser.add_argument("inputfname", type=str, 
            help = "LiDAR file to process.")
        parser.add_argument("destinationpath", type=str, 
            help = "Destination path of output image.")
        parser.add_argument("-r","--aspectratio", help="image aspect ratio",type=float, default=0.0018) 
        parser.add_argument("-v","--verbose",help = "Show intermediate messages.")
        args=parser.parse_args()

        if not os.path.exists(args.inputfname):
            print "ERROR: Input file doesn't exists: {0}.\r\n".format(args.inputfname)
            parser.print_help()
            sys.exit(1)
        return args

    def update_progress(self,progress):
        print '\r[{0}] {1}%'.format('#'*int(progress/10), int(progress)),

    def Execute(self,aspectratio):
        #ratio=imagewidth/float(np.amax(self.inFile.X) - np.amin(self.inFile.X))
        imagewidth=int(aspectratio*(np.amax(self.inFile.X) - np.amin(self.inFile.X)))
        imageheight=int(aspectratio*(np.amax(self.inFile.Y) - np.amin(self.inFile.Y)))
        X=self.inFile.X-np.amin(self.inFile.X)
        X = np.around(X * aspectratio).astype(int)-1
        Y=self.inFile.Y-np.amin(self.inFile.Y)
        Y = np.around(Y * aspectratio).astype(int)-1
        Z=self.inFile.Z-np.amin(self.inFile.Z)
        self.image = np.zeros(shape=(imageheight,imagewidth), dtype = "uint8")
        
        heigth=(255.0/np.amax(Z)*Z).astype(int)

        m=np.column_stack((heigth,X))
        m=np.column_stack((m,Y))
        df=pd.DataFrame(m).sort_values(0)
        i=0
        total=len(df)
        for row in df.itertuples():
            self.image[row[3],row[2]]=row[1]
            if self.verbose > 0:
                if (i % 1000000) == 0:
                    self.update_progress(float(i)/total*100)
            i+=1
        self.update_progress(100.0)
        print('')

    def Close(self,destinationpath):
        outputfname=destinationpath + ('\\' if destinationpath[-1:] != '\\'  else '')+os.path.splitext(os.path.basename(self.inFile.filename))[0]+'.png'
        if args.verbose > 0:
            print('Saving {0}:'.format(outputfname))
        cv2.imwrite(outputfname,self.image)
        self.inFile.close()
       
if __name__ == "__main__":
    args=las2img.ProcessCmdLine()
    l2i = las2img(args.inputfname,args.verbose)
    if args.verbose > 0:
        las2img.Header()
    l2i.Execute(args.aspectratio)
    l2i.Close(args.destinationpath)
    if args.verbose > 0:
        print('Done.')
