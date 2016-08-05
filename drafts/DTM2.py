# -*- coding: utf-8 -*-
# http://www.sciencedirect.com/science/article/pii/S092427161300186X

import os.path
import time
import argparse
from argparse import RawTextHelpFormatter
import numpy as np
import math
from laspy import file
import warnings
from matplotlib import pyplot

def processCell(lasfilename,cellsize):
    inFile = file.File(lasfilename, mode = "r")

    xMin = inFile.x.min()
    xMax = inFile.x.max()
    yMin = inFile.y.min()
    yMax = inFile.y.max()

    step = math.ceil(xMax - xMin) / cellsize
    cell_grid_x,cell_grid_y,cell_grid_z = np.empty([int(step),int(step)]),np.empty([int(step),int(step)]),np.empty([int(step),int(step)])
    
    for stepX in range(int(step)):                 # Looping over the lines
        for stepY in range(int(step)):             # Looping over the columns
            xmin, ymin, xmax, ymax = xMin + (stepX * cellsize), yMin + (stepY * cellsize), xMin + ((stepX + 1) * cellsize), yMin + ((stepY + 1) * cellsize)
            X_valid = np.logical_and(inFile.x >= xmin,
                                      inFile.x < xmax)
            Y_valid = np.logical_and(inFile.y >= ymin,
                                     inFile.y < ymax)
            logicXY = np.logical_and(X_valid, Y_valid)
            validXY = np.where(logicXY)   
            cell_grid_z[stepX,stepY] = inFile.z[validXY].min()
            cell_grid_x[stepX,stepY] = xmin + step/2
            cell_grid_y[stepX,stepY] = ymin + step/2

    print cell_grid_z
    
    pyplot.figure()
    pyplot.scatter(cell_grid_x,cell_grid_y,cell_grid_z)
    pyplot.show()

if __name__ == "__main__":
    lasfname=r"G:\TRANSECTS\T_002\NP_T-002_LAS\6_2_NP_T-002.LAS"
    processCell(lasfname,5)