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
    print("LiDAR file checker v0.8")
    print

def ParseCmdLine():
    parser = argparse.ArgumentParser(description="Validate LAS files.",formatter_class=RawTextHelpFormatter)
    parser.add_argument("inputfname",help="las file to be processed.")
    parser.add_argument("-l","--lasversion", help="LAS file version.", default = None)
    parser.add_argument("-m","--minimumpointsdensity", help="Minimum points density in cloud", required=True)
    parser.add_argument("-d","--displayheader", help="Display LAS file header information", type=int, default = False)
    parser.add_argument("-c","--processorcores", type=int, help="Processor cores to use.", default = 1)
    parser.add_argument("-z","--cellsize", type=int, help="Size (in the same LAS distance unit) of the cell to be checked.",default = -1)
    parser.add_argument("-x","--maxpercentcellsbelowdensity", type=float, help="Maximum percent of cells below points density.", default = -1.0)
    parser.add_argument("-v","--verbose", type=int, help="Level of processing messages.", default = False)
    return parser.parse_args()
    
def ProcessFile(inputfname,lasversion,minimumpointsdensity,displayheader,cellsize,maxpercentcellsbelowdensity,verbose):
    Validate.version = lasversion
    Validate.minimumpointsdensity = minimumpointsdensity
    Validate.displayheader = displayheader
    Validate.cellsize = cellsize
    Validate.cellsize = cellsize
    Validate.maxpercentcellsbelowdensity = maxpercentcellsbelowdensity
    Validate.verbose = verbose
    start = time.time()
    failCount=0
    if(Validate.displayheader):
        lidarutils.displayInfo(inputfname)
    parameters = valParameters()
    validate = Validate(inputfname,parameters)
    failCount+=validate.CheckLiDARFileSignature()
    failCount+=validate.CheckFileVersion()
    failCount+=validate.CheckNumberofReturns()
    failCount+=validate.CheckMinMaxValues()
    validate.CreateShpFileLAS()
    validate.RunCatalog()
    validate.CalcShapeFileArea()
    failCount+=validate.CheckGlobalPointsDensity()
    if (cellsize > 0) and (maxpercentcellsbelowdensity > 0):
        failCount+=validate.CheckMaxCellsBelowDensity()
    if Validate.verbose > 0:
        if(failCount == 0):
            print("All validations passed successfully.")
        else:
            print("{0} validation(s) failed.".format(failCount))
            print(validate.errorMessages)
    print("File: {0},".format(inputfname)),
    print("{0} (elapsed time: {1:.2f}s)".format("ok" if failCount == 0 else "failed: "+validate.errorMessages.strip(),time.time()-start))
       
# In[ ]:

if __name__ == "__main__":
    Header()
    args=ParseCmdLine()
    path, filemask = os.path.split(args.inputfname)
    files=sorted(Validate.FindFiles(path,filemask))
    if len(files) == 0:
        print("There's no file to process.")
        sys.exit(1)
    verystart = time.time()
    print("Processing {0} files.".format(len(files)))
    threads=args.processorcores
    jobs=[]
    i=0

    while i < (len(files) / threads * threads):
        if threads == 1:
            ProcessFile(files[i],args.lasversion,args.minimumpointsdensity,args.displayheader,args.cellsize,args.maxpercentcellsbelowdensity,args.verbose)
            i+=1
            continue
        startpool = time.time()
        p=Pool(threads)
        for thread in range(0,threads):
            params=(files[i + thread],args.lasversion,args.minimumpointsdensity,args.displayheader,args.cellsize,args.maxpercentcellsbelowdensity,args.verbose)
            p=Process(target=ProcessFile,args=params)
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        print("Pool elapsed time: {0:.2f}s".format(time.time()-startpool))    
        i+=threads
    while i < len(files):
        params=(files[i],args.lasversion,args.minimumpointsdensity,args.displayheader,args.cellsize,args.maxpercentcellsbelowdensity,args.verbose)
        if threads == 1:
            ProcessFile(files[i],args.lasversion,args.minimumpointsdensity,args.displayheader,args.cellsize,args.maxpercentcellsbelowdensity,args.verbose)    
            i+=1    
            continue        
        startpool = time.time()
        p=Process(target=ProcessFile,args=params)    
        jobs.append(p)
        p.start()
        i+=1
    for proc in jobs:
        proc.join()
    if threads > 1:
        print("Pool elapsed time: {0:.2f}s".format(time.time()-startpool))    
    totalelapsedtime=time.time()-verystart
    print("Total elapsed time: {0:.2f}s, time/file: {1:.2f}".format(totalelapsedtime,totalelapsedtime/len(files)))
