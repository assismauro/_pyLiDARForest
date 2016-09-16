# -*- coding: utf-8 -*-
import os
import sys
import argparse
import math
import numpy as np
import laspy
#import lidarutils

class calcParams(object):

    def __init__(self, inputfname, verbose):
        self.inputfname = inputfname
        try:
            self.inFile = laspy.file.File(self.inputfname, mode = 'r')
            self.verbose=verbose
        except:
            print("Impossible to open file {0}".format(self.inputfname))
            raise

    @staticmethod
    def Header():
        print("CalcParams v0.8")
        print("")
        print("Processing...")

    def Close(self,csvresults,results):
        if csvresults != None:
            try:
                with open(csvresults,'a') as csv:
                    line=self.inputfname+','
                    for i in range(len(results)):
                        line+=str(results[i])+','
                    csv.write(line[:-1]+'\n')
                    csv.close()
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

    @staticmethod
    def CreateCsv(csvresults,activecalc):
        csv=open(csvresults,'w')
        line='LAS_file,'
        for i in range(len(activecalc)):
            line+=str(activecalc[i])+','
        csv.write('{0}'.format(line[:-1]))
        csv.close()

    @staticmethod
    def ProcessCmdLine():
        #G:\TRANSECTS\T_002\NP_T-002_LAS\np_t-002.las -c 100 -ac 2 -rn 4 -csv E:\mauro.assis\Software\pyLiDARForest\stuff\calcresult2.csv -v 1
        parser = argparse.ArgumentParser(description="Calculate LiDAR params.")
        parser.add_argument("inputfname", type=str, 
            help = "LiDAR file to process.")
        parser.add_argument("-c","--cellsize", help="Cell size.", type =int, default=-1)
        parser.add_argument("-rn","--minreturnnumber", help="Minimun return number to be considered.", type =int, default=4)
        parser.add_argument("-v","--verbose",help = "Show intermediate messages.")
        parser.add_argument('-csv','--csvresults', help='Create and populate a csv file containing data about files and calc results.', type=str, default = None)
        parser.add_argument('-ac','--activecalcs',type=str,default=None,help='''
    Select calcs to run (by number):
    1 - Calculate cells std deviation
    2 - Calculate last returns cloud std deviation

    Ex: -sv 1,2
    ''')
        try:
            return parser.parse_args()
        except:
            raise Exception(sys.exc_info()[0])

        if not os.path.exists(args.inputfname):
            raise Exception("ERROR: Input file doesn't exists: {0}.\r\n".format(args.inputfname))
        return args

    def getCellGenerator(self,points,cellsize,numberofcells=-1): # TODO: define param numberofcells   
        accepted_logic = []              # List to save the true/false for each looping
        maxStep = []                     # List to save the number of cells in X and Y dimension of original data

        cellsizeX = 0.0
        cellSizeY = 0.0

        xmin = points.x.min()
        xmax = points.x.max()
        ymin = points.y.min()
        ymax = points.y.max()

        if(numberofcells > 0):
            cellsizeX = math.ceil((xmax - xmin) / numberofcells / 2) 
            cellsizeY = math.ceil((ymax - ymin) / numberofcells / 2)
            maxStep.append(numberofcells / 2)
            maxStep.append(numberofcells / 2)
        else:
            cellsizeX = cellsize
            cellsizeY = cellsize
            maxStep.append(math.ceil((xmax - xmin) / cellsizeX))
            maxStep.append(math.ceil((ymax - ymin) / cellsizeY))

        if self.verbose:
            print("The original cloud was divided in {0} by {1} cells.".format(maxStep[0],maxStep[1]))

    # In[44]:

        n = 0
        for stepX in range(int(maxStep[0])):                 # Looping over the lines
            for stepY in range(int(maxStep[1])):             # Looping over the columns
                # Step 1 - Filter data from the analized cell
                # Return True or False for return inside the selected cell

                X_valid = np.logical_and((points.x >= xmin + (stepX * cellsizeX)),
                                     (points.x < xmin + ((stepX + 1) * cellsizeX)))
                Y_valid = np.logical_and((points.y >= ymin + (stepY * cellsizeY)),
                                     (points.y < ymin + ((stepY + 1) * cellsizeY)))
                logicXY = np.logical_and(X_valid, Y_valid)
                validXY = np.where(logicXY)

                # show progress before 'continue'
                n += 1
                if(self.verbose):
                     percent = n/(maxStep[0] * maxStep[1])
                     hashes = '#' * int(round(percent * 20))
                     spaces = ' ' * (20 - len(hashes))
                     print("\r[{0}] {1:.2f}%".format(hashes + spaces, percent * 100)),

                if(len(validXY[0]) == 0):
                    accepted_logic.append(False)
                    if(self.verbose):
                        print("Cell {0},{1} has no points.".format(stepX,stepY))
                    continue
            
                Z = points.Z[validXY]
                yield Z

# In[ ]:   

    def calcStdCells(self,cellsize,minreturnnumber):
        means=[]
        Z_valid = np.greater_equal(self.inFile.return_num,minreturnnumber)
        points = self.inFile.points[Z_valid]
        getCell=self.getCellGenerator(points,cellsize)
        for Z in getCell:
            means.append(np.mean(Z))
        return np.std(np.array(means))

    def calcStdLastReturns(self,minreturnnumber):
        Z_valid = np.greater_equal(self.inFile.return_num,minreturnnumber)
        Z = self.inFile.Z[Z_valid]
        return np.std(Z)

if __name__ == "__main__":
    try:
        args=calcParams.ProcessCmdLine()
    except Exception as e:
        print("Unexpected error:", sys.exc_info()[0])
        print e
        sys.exit(1)
    if args.activecalcs == None:
        activecalcs='1,2'
    else:
        activecalcs=args.activecalcs
    activecalcs=map(int,activecalcs.split(','))  
#    if (args.csvresults != None):
#        calcParams.CreateCsv(args.csvresults,activecalcs)
    calc = calcParams(args.inputfname,args.verbose)
    
    results = []
    if(1 in activecalcs):
        results.append(calc.calcStdCells(args.cellsize,args.minreturnnumber))
    if(2 in activecalcs):
        results.append(calc.calcStdLastReturns(args.minreturnnumber))
    if args.csvresults != None:
        try:
            calc.Close(args.csvresults,results)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise