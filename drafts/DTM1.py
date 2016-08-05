# -*- coding: utf-8 -*-
# http://www.sciencedirect.com/science/article/pii/S092427161300186X

import numpy as np
import math
from laspy import file
import warnings
from osgeo import ogr
import shapefile

def shp2wkt(shpfname):
    shp=shapefile.Reader(shpfname).shapes()[0]
    wkt="POLYGON (("
    for i in range(len(shp.points)):
        wkt+="{0} {1},".format(shp.points[i][0],shp.points[i][1])
    return wkt[:-1]+"))"

def splitCells(lasfname, shpfname, cellsize, verbose=0):
    inFile = file.File(lasfname, mode = "r")
    accepted_logic = []              # List to save the true/false for each looping
    maxStep = []                     # List to save the number of cells in X and Y dimension of original data
    warningMsg = []    
    
    cellsizeX = 0.0
    cellSizeY = 0.0

    xMin = inFile.x.min()
    xMax = inFile.x.max()
    yMin = inFile.y.min()
    yMax = inFile.y.max()

    maxStep.append(math.ceil((xMax - xMin) / cellsize))
    maxStep.append(math.ceil((yMax - yMin) / cellsize))

    shpwkt=shp2wkt(shpfname)
    tsctpoly=ogr.CreateGeometryFromWkt(shpwkt)

# In[44]:
    
    n = 0
    for stepX in range(int(maxStep[0])):                 # Looping over the lines
        for stepY in range(int(maxStep[1])):             # Looping over the columns

            xmin, ymin, xmax, ymax = xMin + (stepX * cellsize), yMin + (stepY * cellsize), xMin + ((stepX + 1) * cellsize), yMin + ((stepY + 1) * cellsize)
            sqwkt = "POLYGON (({0} {1}, {2} {1}, {2} {2}, {0} {1}))".format(xmin, ymin, xmax, ymax)
            sqpoly = ogr.CreateGeometryFromWkt(sqwkt)
            
            intersection = tsctpoly.Intersection(sqpoly)

            if intersection == None:
                continue

            X_valid = np.logical_and(inFile.x >= xmin,
                                      inFile.x < xmax)
            Y_valid = np.logical_and(inFile.y >= ymin,
                                     inFile.y < ymax)
            logicXY = np.logical_and(X_valid, Y_valid)
            validXY = np.where(logicXY)

            # show progress before 'continue'
            n += 1
            if(verbose):
                 percent = n/(maxStep[0] * maxStep[1])
                 hashes = '#' * int(round(percent * 20))
                 spaces = ' ' * (20 - len(hashes))
                 print("\r[{0}] {1:.2f}%".format(hashes + spaces, percent * 100)),

            if(len(validXY[0]) == 0):
                accepted_logic.append(False)
                if(verbose):
                    warningMsg.append("Cell {0},{1} has no points, corresponding file was not created.".format(stepX,stepY))
                continue
            
            points = inFile.points[validXY]
# In[48]:
    inFile.close()

if __name__ == "__main__":
    lasfname=r"G:\TRANSECTS\T_002\NP_T-002_LAS\NP_T-002.LAS"
    shpfname=r"G:\TRANSECTS\T_002\POLIGONO_T-002_SHP\POLIGONO_T-002.SHP"
    splitCells(lasfname,shpfname,20)