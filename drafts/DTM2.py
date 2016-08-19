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
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import scipy.linalg
import pandas as pd
from scipy.interpolate import griddata
from scipy.interpolate import interp1d
from scipy.interpolate import UnivariateSpline


def processTiles(csvfilename, xtilesize, ytilesize): #allocates min and max values for x,y for each tile

    cloud = np.genfromtxt(csvfilename, delimiter=',')
   
    cloud_xmax, cloud_ymax, cloud_xmin, cloud_ymin = cloud[:,0].max(), cloud[:,1].max(), cloud[:,0].min(), cloud[:,1].min()

    #to ensure end tiles are big enough
    if (cloud_xmax - cloud_xmin) % xtilesize < 50:
        print 'x tilesize not allowed'
    if (cloud_ymax - cloud_ymin) % ytilesize < 50:
        print 'y tilesize not allowed'
    if (cloud_xmax - cloud_xmin)  % xtilesize > 50 and (cloud_ymax - cloud_ymin) % ytilesize > 50:
        xtiles = int(np.ceil((cloud_xmax - cloud_xmin) / xtilesize)) #number of tiles along x
        ytiles = int(np.ceil((cloud_ymax - cloud_ymin) / ytilesize)) #number of tiles along y
        
        #create array containing x and y min values for each tile   
        x_Min, x_Max, y_Min, y_Max =  np.empty(xtiles*ytiles), np.empty(xtiles*ytiles), np.empty(xtiles*ytiles), np.empty(xtiles*ytiles) 
        count = 0    
        for i in range(xtiles):
            for j in range(ytiles):
                x_Min[count],  y_Min[count]= xtilesize*i, ytilesize*j  
                if i != xtiles - 1: #end tiles are smaller than embedded tiles
                    x_Max[count]= xtilesize*(i+1)
                else:
                    x_Max[count] = cloud_xmax
                if j != ytiles - 1:
                    y_Max[count] = ytilesize*(j+1)
                else:
                    y_Max[count] = cloud_ymax
                count = count + 1
        
        numTiles = len(x_Min) 

        return cloud, x_Min, x_Max, y_Min, y_Max, numTiles 
            

def processCellsNew(cloud, tile, cellsize, x_Min, x_Max, y_Min, y_Max): #splits tile into cells and assigns elevation of each cell as the lowest point in cell, with x,y coordinates at the centre of the cell

    xMin, xMax, yMin, yMax = x_Min[tile], x_Max[tile], y_Min[tile], y_Max[tile] #redifine x,y limits of tile 
    stepsX = int(math.ceil(xMax - xMin) / cellsize)
    stepsY = int(math.ceil(yMax - yMin) / cellsize)
    cell_grid = np.array([[[0]*3]*stepsY]*stepsX, dtype='d')
    tilecoords = cloud[(cloud[:,0] >= xMin) & (cloud[:,0] < xMax) & (cloud[:,1] >= yMin) & (cloud[:,1] < yMax), :]
    
    for stepX in range(stepsX):
        for stepY in range(stepsY):
            xmin, ymin, xmax, ymax = xMin + (stepX * cellsize), yMin + (stepY * cellsize), xMin + ((stepX + 1) * cellsize), yMin + ((stepY + 1) * cellsize)
            cell = tilecoords[(tilecoords[:,0] >= xmin) & (tilecoords[:,0] < xmax) & (tilecoords[:,1] >= ymin) & (tilecoords[:,1] < ymax), :]

            cell_grid[stepX][stepY] = [xmin + cellsize/2, ymin + cellsize/2, cell[:,2].min()]

    cells = np.array(cell_grid.reshape(stepsX*stepsY, 3))  

    #divide into four and filter cells to remove points more than sd_filter standard deviations from the mean
    cells1 = cells[(cells[:,0] <= (xMin + xMax)/2) & (cells[:,1] <= (yMin + yMax)/2), :]
    cells2 = cells[(cells[:,0] > (xMin + xMax)/2) & (cells[:,1] <= (yMin + yMax)/2), :]
    cells3 = cells[(cells[:,0] <= (xMin + xMax)/2) & (cells[:,1] > (yMin + yMax)/2), :]
    cells4 = cells[(cells[:,0] > (xMin + xMax)/2) & (cells[:,1] > (yMin + yMax)/2), :]    
    cells1 = cells1[cells1[:,2] < np.mean(cells1[:,2]) + (np.std(cells1[:,2]))*sd_filter, :]
    cells2 = cells2[cells2[:,2] < np.mean(cells2[:,2]) + (np.std(cells2[:,2]))*sd_filter, :]
    cells3 = cells3[cells3[:,2] < np.mean(cells3[:,2]) + (np.std(cells3[:,2]))*sd_filter, :]
    cells4 = cells4[cells4[:,2] < np.mean(cells4[:,2]) + (np.std(cells4[:,2]))*sd_filter, :]
    #cells_single = cells[cells[:,2] < np.mean(cells[:,2]) + (np.std(cells[:,2]))*sd_filter, :]

    cells = np.vstack((cells1, cells2, cells3, cells4))

    return cell_grid, cells, xMin, xMax, yMin, yMax, stepsX, stepsY


def linFit(cells): #applies linear fit to cells and computes associated r^2
    A = np.c_[cells[:,0], cells[:,1], np.ones(len(cells[:,0]))] #creates matrix to solve
    linC,_,_,_ = scipy.linalg.lstsq(A, cells[:,2]) 
    lin_fitZ = linC[0]*cells[:,0] + linC[1]*cells[:,1] + linC[2] #linC contains linear model parameters

    #plotScatt_Surf3D(cells[:,0], cells[:,1], cells[:,2], lin_fitZ, 'Linear fit')     

    #computing r^2 
    rss = ((cells[:,2] - lin_fitZ)**2).sum()
    tss = ((cells[:,2] - cells[:,2].mean())**2).sum()
    r2_linear = 1 - rss/tss
      
    return r2_linear, lin_fitZ, linC


def quadraticFit(cells): #applies quadratic fit to cells and computes associated r^2
    A = np.c_[np.ones(len(cells[:,0])), cells[:,0], cells[:,1],  cells[:,0]*cells[:,1], cells[:,0]**2, cells[:,1]**2]
    quadC,_,_,_ = scipy.linalg.lstsq(A, cells[:,2])   
    quad_fitZ = quadC[0] + quadC[1]*cells[:,0] + quadC[2]*cells[:,1]  + quadC[3]*cells[:,0]*cells[:,1] + quadC[4]*(cells[:,0]**2) + quadC[5]*(cells[:,1]**2) #quadC contains quadratic model parameters

    #plotScatt_Surf3D(cells[:,0], cells[:,1], cells[:,2], quad_fitZ, 'Linear fit')     

    #computing r^2 
    rss = ((cells[:,2] - quad_fitZ)**2).sum()
    tss = ((cells[:,2] - cells[:,2].mean())**2).sum()
    r2_quadratic = 1 - rss/tss

    return r2_quadratic, quad_fitZ, quadC


def residuals(cells,fit): #divide into sets A and B, A is ground points, B is to be determined
    residuals = np.c_[cells,cells[:,2] - fit] #adding a column for residuals
    setA = residuals[residuals[:,3]<=0,:]
    setB = residuals[residuals[:,3]>0,:]
    return setA, setB


def linsortSetB(lin_setA, lin_setB, r2_linear): #SetC is ground points after full filtering: function sorts setB into ground points and non-ground points. 
    lin_setB = lin_setB[lin_setB[:,3].argsort()][::-1] #sort in order of descending residual
    ground_indices = []
    for i in range(0,len(lin_setB)):
        lin_setD = np.row_stack((lin_setA, np.delete(lin_setB,(i),axis=0))) #cells of entire tile except cell being examined
        r2_linear_run, lin_fitZ, linC = linFit(lin_setD)
        if r2_linear_run <= r2_linear: #if the fit works better with this cell included then the cell is assumed a ground point
            ground_indices.append(i) #cells in setB that when removed from the fit, reduce the r^2 value and retained. Others are discarded
    lin_setC = np.row_stack((lin_setA,lin_setB[ground_indices])) #ground points after full filtering

    r2_linear_run, lin_fitZ, linC = linFit(lin_setC)

    return lin_setC, r2_linear_run, linC    


def quadsortSetB(quad_setA, quad_setB, r2_quadratic): #SetC is ground points after full filtering: function sorts setB into ground points and non-ground points. 
    quad_setB = quad_setB[quad_setB[:,3].argsort()][::-1] #sort in order of descending residual
    ground_indices = []
    for i in range(0,len(quad_setB)):
        quad_setD = np.row_stack((quad_setA, np.delete(quad_setB,(i),axis=0))) #cells of all of tile except cell being examined
        r2_quadratic_run, quad_fitZ, quadC = quadraticFit(quad_setD)
        if r2_quadratic_run <= r2_quadratic: #if the fit works better with this cell included then the cell is assumed a ground point
            ground_indices.append(i) #cells in setB that when removed from the fit, reduce the r^2 value and retained. Others are discarded
    quad_setC = np.row_stack((quad_setA, quad_setB[ground_indices])) #ground points after full filtering

    r2_quadratic_run, quad_fitZ, quadC = quadraticFit(quad_setC)

    return quad_setC, r2_quadratic_run, quadC   


def DTMinterpolation(mparameters, resolution, setC, xMin, xMax, yMin, yMax): #creates DTM at given resolution for data that fitted a model.
    
    gridsX = int(math.ceil(xMax - xMin) / resolution)
    gridsY = int(math.ceil(yMax - yMin) / resolution)
    DTM = np.empty([gridsX*gridsY,3])
    count = 0 
    
    for stepX in range(gridsX):                 # Looping over the lines
        for stepY in range(gridsY):             # Looping over the columns
            xmin, ymin, xmax, ymax = xMin + (stepX * resolution), yMin + (stepY * resolution), xMin + ((stepX + 1) * resolution), yMin + ((stepY + 1) * resolution)
            valid = setC[(setC[:,0]>=xmin) & (setC[:,0]<xmax) & (setC[:,1]>=ymin) & (setC[:,1]<ymax), :]
            
            if len(valid) == 0:
                if len(mparameters) == 3: #linear model was selected
                    DTM[count, :] = np.array([xmin + resolution/2, ymin + resolution/2, mparameters[0]*(xmin + resolution/2) + mparameters[1]*(ymin + resolution/2) + mparameters[2]])
                if len(mparameters) == 6: #quadratic model was selected
                    DTM[count, :] = np.array([xmin + resolution/2, ymin + resolution/2, mparameters[0] + mparameters[1]*(xmin + resolution/2) + mparameters[2]*(ymin + resolution/2) + mparameters[3]*(xmin + resolution/2)*(ymin + resolution/2) + mparameters[4]*((xmin + resolution/2)**2) + mparameters[5]*((ymin + resolution/2)**2)])
            else:
                DTM[count, :] = [xmin + resolution/2, ymin + resolution/2, np.min(valid[:,2])]
            count = count + 1

    return DTM


def plotSurf3D(Xdata, Ydata, Zdata, title):
    xyz = {'x': Xdata, 'y': Ydata, 'z': Zdata}

    # put the data into a pandas DataFrame
    df = pd.DataFrame(xyz, index=range(len(xyz['x']))) 

    # re-create the 2D-arrays
    x1 = np.linspace(df['x'].min(), df['x'].max(), len(df['x'].unique()))
    y1 = np.linspace(df['y'].min(), df['y'].max(), len(df['y'].unique()))
    x2, y2 = np.meshgrid(x1, y1)
    z2 = griddata((df['x'], df['y']), df['z'], (x2, y2), method='cubic')

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    surf = ax.plot_surface(x2, y2, z2, rstride=1, cstride=1, cmap='Blues', linewidth=0)
    plt.title(str(title))
    plt.show()


def plotScatt_Surf3D(Xdata, Ydata, Zdata_scatt, Zdata_surf, title):
    xyz = {'x': Xdata, 'y': Ydata, 'z': Zdata_surf}

    # put the data into a pandas DataFrame
    df = pd.DataFrame(xyz, index=range(len(xyz['x']))) 

    # re-create the 2D-arrays
    x1 = np.linspace(df['x'].min(), df['x'].max(), len(df['x'].unique()))
    y1 = np.linspace(df['y'].min(), df['y'].max(), len(df['y'].unique()))
    x2, y2 = np.meshgrid(x1, y1)
    z2 = griddata((df['x'], df['y']), df['z'], (x2, y2), method='cubic')

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(x2, y2, z2, rstride=1, cstride=1, linewidth=0, alpha=0.5)   
    ax.scatter(cells[:,0], cells[:,1], cells[:,2], c='r')    
    plt.title(str(title))
    plt.show()


def slopeCheck(cell_grid, cells, stepsX, stepsY): #if there is a change in gradient along a line along the x or y axis then the elevation of the point at which there is this change is replaced by the average elevation of the points on either side of the line to it
    #order cells into jagged lists sorted for x values (cell_xsort) and y values (cell_ysort)
    cells_xsort, lenx = range(stepsX), np.empty(stepsX)
    for i in range(stepsX):
        cellsx = []
        for j in range(len(cells)):
            if cells[j,0] == cell_grid[i,0,0]:
                cellsx.append(cells[j,:])
        cells_xsort[i] = np.array(cellsx) 
        lenx[i] = len(cells_xsort[i])
    cells_ysort, leny = range(stepsY), np.empty(stepsY)
    for i in range(stepsY):
        cellsy = []
        for j in range(len(cells)):
            if cells[j,1] == cell_grid[0,i,1]:
                cellsy.append(cells[j,:])
        cells_ysort[i] = np.array(cellsy) 
        leny[i] = len(cells_ysort[i])

    #find elevations to replace and find value they need to be replaced by. Replacing along constant x first
    replace_xindices, xreplace = [], []
    for i in range(stepsX):
        for j in range(1, int(lenx[i]-1)):
            if np.sign((cells_xsort[i][j+1][2] - cells_xsort[i][j][2]) / (cells_xsort[i][j+1][1] - cells_xsort[i][j][1])) != np.sign((cells_xsort[i][j][2] - cells_xsort[i][j-1][2]) / (cells_xsort[i][j][1] - cells_xsort[i][j-1][1])):
                replace_xindices.append([i,j,2])
                xreplace.append((cells_xsort[i][j+1][2] + cells_xsort[i][j-1][2]) / 2)
    replace_yindices, yreplace = [], []
    for i in range(stepsY):
        for j in range(1, int(leny[i]-1)):
            if np.sign((cells_ysort[i][j+1][2] - cells_ysort[i][j][2]) / (cells_ysort[i][j+1][0] - cells_ysort[i][j][0])) != np.sign((cells_ysort[i][j][2] - cells_ysort[i][j-1][2]) / (cells_ysort[i][j][0] - cells_ysort[i][j-1][0])):
                replace_yindices.append([i,j,2]) #values to replace along constant y are calculated after values are replaced along constant x

    #replace along constant x lines
    for i in range(len(xreplace)):
        cells_xsort[replace_xindices[i][0]][replace_xindices[i][1]][2] = xreplace[i]
    #convert back into 2D array in order to now replace y indices
    cells_xdone = []
    for i in range(stepsX):
        for j in range(int(lenx[i])):
            cells_xdone.append(cells_xsort[i][j])
    cells_xdone = np.array(cells_xdone)

    #replace along constant y lines
    for i in range(stepsY):
        cellsy = []
        for j in range(len(cells_xdone)):
            if cells_xdone[j,1] == cell_grid[0,i,1]:
                cellsy.append(cells_xdone[j,:])
        cells_ysort[i] = np.array(cellsy) #jagged list sorted for y values, so we can index where to replace  
    for i in range(len(replace_yindices)):
        cells_ysort[replace_yindices[i][0]][replace_yindices[i][1]][2] = (cells_ysort[replace_yindices[i][0]][replace_yindices[i][1]+1][2] + cells_ysort[replace_yindices[i][0]][replace_yindices[i][1]-1][2]) / 2
    #convert back into 2D array for interpolation
    cells_done = []
    for i in range(stepsX):
        for j in range(int(lenx[i])):
            cells_done.append(cells_xsort[i][j])
    cells = np.array(cells_done)

    return cells 


def splineInterpolation(resolution, cell_grid, cells, stepsX, stepsY, xMin, xMax, yMin, yMax):

    #1D cubic spline interpolation across y values (const x) first. Then across x values (const y).
    #set up DTM with y values at desired resolution but x values still separated by previous cell size
    gridsX = int(math.ceil(xMax - xMin) / resolution)
    gridsY = int(math.ceil(yMax - yMin) / resolution)
    DTM_yint = np.array([[[0]*3]*gridsY]*stepsX, dtype='d')
    for stepX in range(stepsX):
        for gridY in range(gridsY):
            DTM_yint[stepX,gridY] = [cell_grid[stepX,0,0], yMin + gridY*resolution + resolution/2, 0] 

    #cubic spline interpolation across y values. Then projected onto grid of required resolution
    #must ensure highest value of y in new grid is less than that in the old grid as spline interpolation cannot extrapolate.

    for x in range(stepsX):
        if DTM_yint[x,gridsY-1,1] < cells[cells[:,0] == cell_grid[x,0,0],1].max() and DTM_yint[x,0,1] > cells[cells[:,0] == cell_grid[x,0,0],1].min(): 
            DTM_yint[x,:,2] = interp1d(cells[cells[:,0] == cell_grid[x,0,0],1], cells[cells[:,0] == cell_grid[x,0,0],2], kind='cubic')(DTM_yint[x,:,1])
        else: #if points we want to find are outside interpolation then we use univaraite spline to extrapolate instead (k=3 for cubic)
            if len(cells[cells[:,0] == cell_grid[x,0,0],1]) > 3:
                DTM_yint[x,:,2] = UnivariateSpline(cells[cells[:,0] == cell_grid[x,0,0],1], cells[cells[:,0] == cell_grid[x,0,0],2], k=3, ext=0)(DTM_yint[x,:,1])
            if 2 < len(cells[cells[:,0] == cell_grid[x,0,0],1]) <= 3:
                DTM_yint[x,:,2] = UnivariateSpline(cells[cells[:,0] == cell_grid[x,0,0],1], cells[cells[:,0] == cell_grid[x,0,0],2], k=2, ext=0)(DTM_yint[x,:,1])
            if 1 < len(cells[cells[:,0] == cell_grid[x,0,0],1]) <= 2:
                DTM_yint[x,:,2] = UnivariateSpline(cells[cells[:,0] == cell_grid[x,0,0],1], cells[cells[:,0] == cell_grid[x,0,0],2], k=1, ext=0)(DTM_yint[x,:,1])

    #set up DTM with y and x values at desired resolution
    DTM = np.array([[[0]*3]*gridsY]*gridsY, dtype='d')
    for gridX in range(gridsX):
        for gridY in range(gridsY):
            DTM[gridX,gridY] = [xMin + gridX*resolution + resolution/2, yMin + gridY*resolution + resolution/2, 0] 

    #cubic spline interpolation across x values. Then projected onto grid of required resolution
    for y in range(gridsY):
        if DTM[gridsX-1,y,0] < cells[cells[:,1] == cell_grid[0,y,1],0].max() and DTM[0,y,0] > cells[cells[:,1] == cell_grid[0,y,1],0].min(): 
            DTM[:,y,2] = interp1d(cells[cells[:,1] == cell_grid[0,y,1],0], cells[cells[:,1] == cell_grid[0,y,1],2], kind='cubic')(DTM[:,y,0])
        else: #if points we want to find are outside interpolation then we use univaraite spline to extrapolate instead
            if len(cells[cells[:,1] == cell_grid[0,y,1],0]) > 3:
                DTM[:,y,2] = UnivariateSpline(cells[cells[:,1] == cell_grid[0,y,1],0], cells[cells[:,1] == cell_grid[0,y,1],2], k=3, ext=0)(DTM[:,y,0])
            if 2 < len(cells[cells[:,1] == cell_grid[0,y,1],0]) <= 3:
                DTM[:,y,2] = UnivariateSpline(cells[cells[:,1] == cell_grid[0,y,1],0], cells[cells[:,1] == cell_grid[0,y,1],2], k=2, ext=0)(DTM[:,y,0])
            if 1 < len(cells[cells[:,1] == cell_grid[0,y,1],0]) <= 2:
                DTM[:,y,2] = UnivariateSpline(cells[cells[:,1] == cell_grid[0,y,1],0], cells[cells[:,1] == cell_grid[0,y,1],2], k=1, ext=0)(DTM[:,y,0])
    DTM = np.array(DTM.reshape(gridsX*gridsY, 3))

    return DTM #create DTM using cubic spline interpolation if neither model fits


def DTMarea(xtilesize, ytilesize):

    if __name__ == "__main__":

        cloud, x_Min, x_Max, y_Min, y_Max, numTiles = processTiles(csvfilename, xtilesize, ytilesize)


        DTMall = np.empty([600,3])
        rows = 0

        for tile in range(numTiles):

            cell_grid, cells, xMin, xMax, yMin, yMax, stepsX, stepsY = processCellsNew(cloud, tile, cellsize, x_Min, x_Max, y_Min, y_Max)
    
            #fitting unfiltered data
            r2_linear, lin_fitZ, linC = linFit(cells) #applying linear fit to unfiltered data
            r2_quadratic, quad_fitZ, quadC = quadraticFit(cells) #applying quadratic fit to unfiltered data
    
            #sorting initially filtered data into sets for further ground filtering
            lin_setA, lin_setB = residuals(cells, lin_fitZ) #sort by residuals of linear fit
            quad_setA, quad_setB = residuals(cells, quad_fitZ) #sort by residuals of quadratic fit
            r2_linear_run, lin_fitZ, linC = linFit(lin_setA) #applying linear fit to filtered data
            r2_quadratic_run, quad_fitZ, quadC = quadraticFit(quad_setA) #applying quadratic fit to filtered data  

            #select better model, assign ground point cells to set C. Then use DTM interpolation    
            lin_setC, r2_linear_run, linC = linsortSetB(lin_setA, lin_setB, r2_linear)
            quad_setC, r2_quadratic_run, quadC = quadsortSetB(quad_setA, quad_setB, r2_quadratic)  
            if r2_linear_run >= r2_threshold or r2_quadratic_run >= r2_threshold:
                if r2_linear_run >= r2_quadratic_run:    
                    print 'Linear model selected for tile, with r^2 = %f after ground filtering process. (threshold r^2 = %f)' %(r2_linear_run, r2_threshold)
                    setC, mparameters = lin_setC[:,(0,1,2)], linC
                if r2_linear_run < r2_quadratic_run:
                    print 'Quadratic model selected for tile, with r^2 = %f after ground filtering process (threshold r^2 = %f)' %(r2_quadratic_run, r2_threshold)
                    setC, mparameters = quad_setC[:,(0,1,2)], quadC
                DTM = DTMinterpolation(mparameters, resolution, setC, xMin, xMax, yMin, yMax)

            #Use spline interpolation
            else:
                print 'Neither linear nor quadratic model fits sufficiently well for use. Spline interpolation required.'
                cells = slopeCheck(cell_grid, cells, stepsX, stepsY)
                DTM = splineInterpolation(resolution, cell_grid, cells, stepsX, stepsY, xMin, xMax, yMin, yMax)
        
            DTMall[rows:(rows+len(DTM)),:] = DTM
            rows = rows + len(DTM)

    return DTMall


#define arguments
csvfilename, r2_threshold, resolution, cellsize, sd_filter = 'cloudsectTransf.csv', 0.95, 10, 7, 1

xtilesize, ytilesize = 100, 100

DTM = DTMarea(xtilesize, ytilesize)

plotSurf3D(DTM[:,0], DTM[:,1], DTM[:,2], 'DTM of tiles')
