#lidarUtils

This library contains a group of routines developed by me & Eric Gorgens to implement some useful features for people that deals with forestry LiDAR clouds.

It can be used as a command line python application:

python lidarutils.py <filename> <options>

or as a library to be imported and used in other python apps.

##features

**def displayHeader(header)**
Display header information of a LAS file

**def splitCells(inputfname, cellsize=-1, numberofcells=-1, verbose=False)**
Split a LAS file in numberofcells cells OR cells of square cellsize area.

**def slices(inputfname,nslices=1,percbottom=-1.0,perctop=-1.0,verbose=True)**
Split a LAS file in vertical nslices vertical slices OR generates a slice excluding percbottom and perctop points

**def toFloor(inputfname,outputfname=None,floor=0.0,verbose=True)**
Set Z coordinate of a LAS file to min Z value, projecting all points to "floor"

**def topBottom(command,inputfname,outputfname=None,cut=None,cutpercent=None,verbose=True)**
Generates a new LAS file excluding points above and below cut OR cutpercent

**def exportToCSV(inputfname,outputfname=None,delimiter=";",verbose=True)**
Export LiDAR file points data to a .CSV file, using delimter to separe column values.

**def displayInfo(inputfname,verbose=True)**
Display header and variable records of inputfname file name

**def projectY(inputfname,outputfname=None,verbose=True)**
Set all Y value to min Y value

**def projectXY(inputfname,outputfname=None,verbose=True)**
Set all Y value to min Y value
NOTE: it´s useful to create a height histogram, f.e.




