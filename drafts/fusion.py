# -*- coding: utf-8 -*-
import os
import sys
import glob
import subprocess
import shutil 
import helper
import argparse
from argparse import RawTextHelpFormatter
   
class fusion(object):
    '''Calculate LiDAR metrics for a cloud using Fusion'''
    def __init__(self, args):
        self.args = args
        self.verbose = args.verbose

    def Outlier(self,args):
# FilterData [switches] FilterType FilterParms WindowSize OutputFile DataFile
# c:\fusion\FilterData outlier 3.0 20 g:\Flt_NP_T-356.las G:\TRANSECTS\T_356\NP_T-356_LAS\NP_T-356.las H:\DebugFiles\flt_NP_T-356.las
        cmd=r'{0}\filterdata.exe {1} {2} {3} {4} {5}'.format(helper.fusionpath, args.filtertype, \
            args.stdmultiplier, args.windowsize, args.outputfname, args.inputfname) 
        if self.verbose:
            print(cmd)
        ret=helper.run_command(cmd)
        if self.verbose:
            print(ret)

    def GroundFilter(self,args):
#    c:\fusion2\GroundFilter C:\LiDAR2\LAS\T_N-356\gdf_NP_T-356.las 5 C:\LiDAR2\LAS\T_N-356\Flt_NP_T-356.las
        cmd=r'{0}\groundfilter.exe {1} {2} {3} {4} {5}'.format(helper.fusionpath, args.filtertype, \
            args.stdmultiplier, args.windowsize, args.outputfname, args.inputfname) 
        if self.verbose:
            print(cmd)
        ret=helper.run_command(cmd)
        if self.verbose:
            print(ret)

    @staticmethod
    def Header():
        print('LiDAR to Image v0.8')
        print('')
        print('Processing...')

    @staticmethod
    def ProcessCmdLine():
        # G:\TRANSECTS\T_356\NP_T-356_LAS\NP_T-356.las g:\flt_NP_T-356.las -t o -ft outlier -ws 20 -stdm 3.0 -v
        parser = argparse.ArgumentParser(description='Calculate LiDAR metrics.')
        parser.add_argument('inputfname', type=str, help = 'LiDAR file to process.')
        parser.add_argument('outputfname', type=str, help = 'Output file name.', default = '')
        parser.add_argument('-t','--task',choices=['o'], required=True, 
          help='''
Define task to be done.
  'o' apply outlier filter
               ''')
        parser.add_argument('-ft','--filtertype', type=str, help='Filter type', default='outlier')
        parser.add_argument('-c','--cellsize', type=float, help='Window size', default=20.0)
        parser.add_argument('-stdm','--stdmultiplier', type=float, help='Window size', default=3.0)
        
        parser.add_argument('-v','--verbose', help='Level of processing messages.', action='store_true', default=False)

        args=parser.parse_args()

        if not os.path.exists(args.inputfname):
            raise Exception('ERROR: Input file doesn''t exists: {0}.\r\n'.format(args.inputfname))
        return args

    def update_progress(self,progress):
        print('\r[{0}] {1}%'.format('#'*int(progress/10), int(progress)),)

    def Execute(self):
        if args.task == 'o':
            self.Outlier(args)

    def Close(self):
        print("Program ended.")

if __name__ == '__main__':
    try:
        args=metrics.ProcessCmdLine()
    except Exception as e:
        print('Unexpected error:', sys.exc_info()[0])
        print e
        sys.exit(1)

    mt = metrics(args)
    if args.verbose:
        metrics.Header()
    mt.Execute()
    mt.Close()
    if mt.verbose > 0:
        print('Done.')
