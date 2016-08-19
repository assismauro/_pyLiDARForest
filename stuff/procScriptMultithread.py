# -*- coding: utf-8 -*-
import os
import traceback
import glob
import argparse
from argparse import RawTextHelpFormatter
import sys
import subprocess

import fnmatch
import time
from multiprocessing import Pool, Process

def Header():
    print('Multithread exec v0.8')
    print

def ParseCmdLine():
    parser = argparse.ArgumentParser(description='Process python scripts in multiprocessing mode.',formatter_class=RawTextHelpFormatter)
    parser.add_argument('programname',help='Python script file')
    parser.add_argument('inputfname',help='las file mask to be processed.')
    parser.add_argument('-c','--processorcores', type=int, help='Processor cores to use.', default = 1)
    parser.add_argument('-o','--otherparams',help='complementary parameters.')
    parser.add_argument("-v","--verbose",type=int, help = "Show intermediate messages.", default = 0)

    return parser.parse_args()

def RunCommand(command, verbose):
    p = subprocess.Popen(command,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)
    out, err = p.communicate()
    if verbose > 0:
        print(out)
    return out, err

def FindFiles(directory, pattern):
    flist=[]
    for root, dirs, files in os.walk(directory):
        for filename in fnmatch.filter(files, pattern):
            flist.append(os.path.join(root, filename))
    return flist

def ProcessFile(program,fname,options,verbose):
    RunCommand('python {0} {1} {2}'.format(program,fname,options), verbose)

if __name__ == '__main__':
    Header()
    args=ParseCmdLine()
    start = time.time()
    failcount=0
    path, filemask = os.path.split(args.inputfname)
    files=sorted(FindFiles(path,filemask))
    if len(files) == 0:
        print('There''s no file to process.')
        sys.exit(1)
    verystart = time.time()
    print('Processing {0} files.'.format(len(files)))
    threads=args.processorcores
    jobs=[]
    i=0

    while i < (len(files) / threads * threads):
        if threads == 1:
            ProcessFile(args.programname,files[i],args.otherparams,args.verbose)
            i+=1
            continue
        startpool=time.time()
        p=Pool(threads)
        for thread in range(0,threads):
            params=(args.programname,files[i + thread],args.otherparams,args.verbose)
            p=Process(target=ProcessFile,args=params)
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        print('Pool elapsed time: {0:.2f}s'.format(time.time()-startpool))    
        i+=threads
    while i < len(files):
        params=(args.programname,files[i],args.otherparams,args.verbose)
        if threads == 1:
            ProcessFile(args.programname,files[i],args.otherparams,args.verbose)    
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
        print('Pool elapsed time: {0:.2f}s'.format(time.time()-startpool))    
    totalelapsedtime=time.time()-verystart
    print('Total elapsed time: {0:.2f}s, time/file: {1:.2f}'.format(totalelapsedtime,totalelapsedtime/len(files)))
