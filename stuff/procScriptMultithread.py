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
    # procScriptMultithread.py E:\mauro.assis\Software\pyLiDARForest\stuff\calcParams.py  g:\transects\np_t-???.las -c 1 -o="-c 100 -ac 2 -rn 4 -csv E:\mauro.assis\Software\pyLiDARForest\stuff\calcresult2.csv" -iscmd 0
    parser = argparse.ArgumentParser(description='Process python scripts in multiprocessing mode.',formatter_class=RawTextHelpFormatter)
    parser.add_argument('programname',help='Python script file')
    parser.add_argument('inputfname',help='File mask to be processed. If txt extension, it will consider as a txt file containing a file names list to be processed.')
    parser.add_argument('-iscmd','--iscommandline', type=int, default=0, help='If 0, execute python script, else run a program (exe file).')
    parser.add_argument('-c','--processorcores', type=int, help='Processor cores to use.', default = 1)
    parser.add_argument('-o','--otherparams',type=str, help='complementary parameters.')
    parser.add_argument("-v","--verbose",type=int, help = "Show intermediate messages.", default = 0)
    try:
        return parser.parse_args()
    except:
        print sys.exc_info()[0]


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

def ProcessFile(program,fname,options,iscmd,verbose):
    RunCommand('{0}{1} {2} {3}'.format(('python ' if iscmd==0 else ''), program,fname,options), verbose)

if __name__ == '__main__':
    Header()
    args=ParseCmdLine()   
    start = time.time()
    failcount=0
    extension = os.path.splitext(args.inputfname)[1]
    if extension.upper() == '.TXT':
        f = open(args.inputfname)
        files = f.readlines()
    else:
        path, filemask = os.path.split(args.inputfname)
        files=FindFiles(path,filemask)
    files = sorted(files)
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
            ProcessFile(args.programname,files[i],args.otherparams,args.iscommandline,args.verbose)
            i+=1
            continue
        startpool=time.time()
        p=Pool(threads)
        for thread in range(0,threads):
            params=(args.programname,files[i + thread],args.otherparams,args.iscommandline,args.verbose)
            p=Process(target=ProcessFile,args=params)
            jobs.append(p)
            p.start()
        for proc in jobs:
            proc.join()
        print('Pool elapsed time: {0:.2f}s'.format(time.time()-startpool))    
        i+=threads
    while i < len(files):
        params=(args.programname,files[i],args.otherparams,args.iscommandline,args.verbose)
        if threads == 1:
            ProcessFile(args.programname,files[i],args.otherparams,args.iscommandline,args.verbose)    
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
