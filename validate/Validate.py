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

class Validate(object):
    version = ""
    minimumpointsdensity = 4.0
    cellsize = -1
    maxpercentcellsbelowdensity = -0.1
    displayheader = False
    cellsize = 10
    verbose = 0   
        
    def __init__(self,inputfname, parameters):
        self.inputfname = inputfname;
        self.inFile = laspy.file.File(self.inputfname, mode = "r")
        self._errorMessages = "" 
        self.parameters = parameters

    @property
    def errorMessages(self):
        return "" if len(self._errorMessages) == 0 else self._errorMessages[:-1]

    def TestOk(self):
        if Validate.verbose > 0:
            print("Test passed.")
            print
        
    def TestFail(self, errormessage):
        self._errorMessages+=errormessage+","
        if Validate.verbose > 0:
            print("Test failed: {0}".format(errormessage))
            print

    @staticmethod
    def FindFiles(directory, pattern):
        flist=[]
        for root, dirs, files in os.walk(directory):
            for filename in fnmatch.filter(files, pattern):
                flist.append(os.path.join(root, filename))
        return flist

    def RunCommand(self,command):
        p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
        return p.communicate()

    def Area(self,corners):
        n = len(corners) - 1 # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1]
            area -= corners[j][0] * corners[i][1]
        return abs(area) / 2.0

    def CheckLiDARFileSignature(self):
        if Validate.verbose > 0:        
            print("LiDAR file signature")
        if self.inFile.header.file_signature != "LASF":
            self.TestFail("Not a valid las file")
            return 1
        self.TestOk()
        return 0
        
    def CheckFileVersion(self):
        if(Validate.version == None and Validate.verbose):
            print("LiDAR file version not specified.")
            return 0
        if Validate.verbose > 0:       
            print("LiDAR file version ({0} expected)".format(Validate.version))
        if self.inFile.header.version != Validate.version:
            self.TestFail("File version is {0} and should be {1}.\r\n".format(self.inFile.header.version,Validate.version))
            return 1
        self.TestOk()
        return 0

    def CheckNumberofReturns(self):        
        if Validate.verbose > 0:        
            print("Check number of points informed in header and existing")
        if self.inFile.header.point_records_count != len(self.inFile.x):
            self.TestFail("There are {0} points indicated by reader and exists {1} points".format(self.inFile.header.point_records_count,len(inFile.x)))
            return 1
        self.TestOk()
        return 0

    def CheckGlobalPointsDensity(self):
        if Validate.verbose > 0: 
            print
            print("Check global point density")
        cloudpointsdensity = self.inFile.header.point_records_count / self.areatransect
        if Validate.verbose > 0:        
            print("Cloud points density: {0}, Minimum expected points density: {1}".format(cloudpointsdensity,Validate.minimumpointsdensity))
        if(cloudpointsdensity < float(Validate.minimumpointsdensity)):
            self.TestFail("Points density below minimum: is {0} and should be at least {1}\r\n".format(cloudpointsdensity,Validate.minimumpointsdensity))
            return 1
        else:
            self.TestOk()
            return 0
                
    def CreateShpFileLAS(self):
        if Validate.verbose > 0:        
            print("Creating boundary shape file")
        return self.RunCommand("{0}lasboundary -i {1} -oshp".format(self.parameters.lastoolspath,self.inputfname))
 
    def CalcShapeFileArea(self):
        if Validate.verbose > 0:        
            print("Calculating shape file area")
        shapefilename=('.').join(self.inputfname.split('.')[:-1])+".shp"
        sf=shapefile.Reader(shapefilename)
        shapes=sf.shapes()
        if len(shapes) != 1:
            raise ValueError("{0} should have one and only one polygon.")
        else:
            self.areatransect=self.Area(shapes[0].points)
            if Validate.verbose > 0:
                print("Area LAS file: {0} ha".format(self.areatransect/10000))

    def RunCatalog(self):
        if Validate.verbose > 0:        
            print("Running Fusion catalog command")
        csvcatalogfname=('.').join(self.inputfname.split('.')[:-1])+".csv"
#        command="{0}catalog /rawcounts /coverage /intensity:1,0,255 /firstdensity:1,{1},{2} /density:1,{1},{2} {3} {4}".format(\
#            self.parameters.fusionpath,minpointsdensity,minpointsdensity * 2,self.inputfname,csvcatalogfname)
#        return self.RunCommand(command)      
        command="{0}catalog /image /density:1,{1},{2} {3} {4}".format(self.parameters.fusionpath,\
        Validate.minimumpointsdensity,float(Validate.minimumpointsdensity) * 2,self.inputfname,csvcatalogfname)        
        return self.RunCommand(command)              
#       catalog /rawcounts /coverage /intensity:1,0,255 /firstdensity:1,4,20 /density:1,4,20

    def CheckMinMaxValues(self):
        if Validate.verbose > 0:                
            print("Check min and max X,Y,Z values in header against 'real' values in file")
#        print("Header bounding box:")
#        bb = zip(["X", "Y", "Z"], self.inFile.header.min, self.inFile.header.max)
#        for i in bb:
#            print("..." + str(i))
        errorMsg=""
        x_invalid = np.logical_or((self.inFile.x - self.inFile.header.min[0]) < -0.01,\
            (self.inFile.x - self.inFile.header.max[0]) > 0.01)
        bad_x = np.where(x_invalid)
        if len(bad_x) == 0:
            errorMsg+="There are x coordinates that are not between header.min[0] and header.max[0]\r\n"
        y_invalid = np.logical_or((self.inFile.y - self.inFile.header.min[1]) < -0.01,\
            (self.inFile.y - self.inFile.header.max[1]) > 0.01)
        bad_y = np.where(y_invalid)
        if len(bad_y) == 0:
            errorMsg+="There are y coordinates that are not between header.min[1] and header.max[1]\r\n"
        z_invalid = np.logical_or((self.inFile.z - self.inFile.header.min[2]) < -0.01,\
            (self.inFile.x - self.inFile.header.max[2]) > 0.01)
        bad_z = np.where(z_invalid)
        if len(bad_z) == 0:
            errorMsg+="There are z coordinates that are not between header.min[2] and header.max[2]\r\n"
        if(float(self.inFile.header.version) >= 1.3):
            minX_t = min(self.inFile.x_t)
            maxX_t = max(self.inFile.x_t)
            minY_t = min(self.inFile.y_t)
            maxY_t = max(self.inFile.y_t)
            minZ_t = min(self.inFile.z_t)
            maxZ_t = max(self.inFile.z_t)
            errorMsg1=""
            if np.isnan(minX_t) or np.isinf(minX_t):
                errorMsg1="\r\nMin(Xt) is not valid,"
            if np.isnan(minY_t) or np.isinf(minY_t):
                errorMsg1+="Min(Yt) is not valid,"
            if np.isnan(minZ_t) or np.isinf(minZ_t):
                errorMsg1+="Min(Zt) is not valid,"
            if (self.verbose > 0) and (errorMsg1 == ""):
                try:
                    print("Validate Xt, Yt, Zt\r\n"+\
                    "     Min            Max\r\n"+\
                    "Xt:  {0:%.3E}        {1:%.3E}\r\n".format(minX_t,maxX_t)+\
                    "Yt:  {0:%.3E}        {1:%.3E}\r\n".format(minY_t,maxY_t)+\
                    "Zt:  {0:%.3E}        {1:%.3E}\r\n".format(minZ_t,maxZ_t))
                except:
                    pass
            if len(errorMsg1) > 0:
                errorMsg+=errorMsg1[:-1]
        if len(errorMsg) != 0:
            self.TestFail(errorMsg)
            return 1
        self.TestOk()
        return 0

    def CheckMaxCellsBelowDensity(self):
        if Validate.verbose > 0:                
            print("Check points density per area unit, showing the percent of area units below the limit")    
        try:
            fName=self.inFile.filename.upper().replace(".LAS",".HTML")
            fstr=open(fName,"r").read().replace("\r","").replace("\n","")
            fstr=fstr[fstr.index("Density less than minimum specification"):]
            fstr=fstr[fstr.index("%\">"):]
            percentualbelow=float(fstr[3:fstr.index("<")])
        except Exception, e:
            self.TestFail("Impossible to check density value in {0} ".format(fName))
            return 1
        if percentualbelow > self.maxpercentcellsbelowdensity:
            self.TestFail("Points density above maximum: is {0} and should be lower than {1}\r\n".format(percentualbelow,Validate.maxpercentcellsbelowdensity))
            return 1
        else:
            self.TestOk()
            return 0
    
    # not finished!
    def CheckMaxCellsBelowDensity1(self):
        if Validate.verbose > 0:                
            print("Check points density per area unit, showing the percent of area units below the limit")    
        accepted_logic = []              # List to save the true/false for each looping
        maxStep = []                     # List to save the number of cells in X and Y dimension of original data
        warningMsg = []    
    
        cellsizeX = 0.0
        cellSizeY = 0.0

        xmin = self.inFile.x.min()
        xmax = self.inFile.x.max()
        ymin = self.inFile.y.min()
        ymax = self.inFile.y.max()

        cellsizeX = Validate.cellsize
        cellsizeY = Validate.cellsize
        maxStep.append(math.ceil((xmax - xmin) / cellsizeX))
        maxStep.append(math.ceil((ymax - ymin) / cellsizeY))

# In[44]:

        n = 0
        cellsabove = 0
        cellsbelow = 0
        points = 0
        for stepX in range(int(maxStep[0])):                 # Looping over the lines
            for stepY in range(int(maxStep[1])):             # Looping over the columns
            # Step 1 - Filter data from the analized cell
            # Return True or False for return inside the selected cell

                X_valid = np.logical_and((self.inFile.x >= xmin + (stepX * cellsizeX)),
                                 (self.inFile.x < xmin + ((stepX + 1) * cellsizeX)))
                Y_valid = np.logical_and((self.inFile.y >= ymin + (stepY * cellsizeY)),
                                 (self.inFile.y < ymin + ((stepY + 1) * cellsizeY)))
                logicXY = np.logical_and(X_valid, Y_valid)
                validXY = np.where(logicXY)

                points = len(validXY[0])
                if points > 0:
                    if points >= Validate.minimumpointsdensity:
                        cellsabove += 1
                    else:
                        cellsbelow += 1

                # show progress
                n += 1
                if(Validate.verbose):
                    percent = n/(maxStep[0] * maxStep[1])
                    hashes = '#' * int(round(percent * 20))
                    spaces = ' ' * (20 - len(hashes))
                    print("\r[{0}] {1:.2f}%".format(hashes + spaces, percent * 100)),

        if (cellsbelow / (cellsbelow + cellsabove) > Validate.maxpercentcellsbelowdensity):
            self.TestFail(errorMsg)
            return 1
        else:
            self.TestOk()

