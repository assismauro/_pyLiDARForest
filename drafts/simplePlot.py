import pyqtgraph as pg
import pyqtgraph.opengl as gl
import lasFWF
import numpy as np

### something to graph ######
from numpy import *
pi=3.1415
X=linspace(-10,10,100)
Y1=2+sin(X)
Y2=-2+Y1*Y1
Y3=cos(1*Y1)/(X+0.0131415)
Y4=4+sin(X)*cos(2*X)
Z=exp(-0.1*X*X)*cos(0.3*(X.reshape(100,1)**2+X.reshape(1,100)**2))
#############################
# you need this call ONCE 
app=pg.QtGui.QApplication([])
#############################
'''
##### plot 3D surface data  ####
w = gl.GLViewWidget()
## Saddle example with x and y specified
p = gl.GLSurfacePlotItem(x=X, y=X, z=Z, shader='heightColor')
w.addItem(p)
# show
w.show()
pg.QtGui.QApplication.exec_()
'''
#==============================================

##### plot 3D line data  ####
w = gl.GLViewWidget()
# first line
Z=zeros(size(X))
p=array([X,Y2,Z])
p=p.transpose() 
C=pg.glColor('w')
###### SCATTER ######
plt = gl.GLScatterPlotItem(pos=p, color=C)
#w.addItem(plt)

# second line
Z=zeros(size(X))
p=array([X,Z,Y3])
p=p.transpose() 
C=pg.glColor('b')
######## LINE  ############
plt = gl.GLLinePlotItem(pos=p, width=20.5,color=C)
#w.addItem(plt)

# third line
Z=zeros(size(X))
p=array([Z,Y1,X])
p=p.transpose() 
C=pg.glColor('g')
########### SCATTER #############
plt = gl.GLScatterPlotItem(pos=p, color=C, size=3)
#w.addItem(plt)


############# GRID #################
fwf=lasFWF.FWFFile(r'D:\CCST\Data\T_356\NP_T-356_FWF_LAS\NP_T-356_FWF.LAS')
'''
Z=fwf.Z[1:1000]
Y=fwf.Y[1:1000]
X=fwf.X[1:1000]
'''

Z=(fwf.Z-np.amin(fwf.Z))/10
Y=(fwf.Y-np.amin(fwf.Y))/10
X=(fwf.X-np.amin(fwf.Z))/10

p=array([Z,Y,X])
Z=[]
Y=[]
X=[]
p=p.transpose() 
C=pg.glColor('b')
########### SCATTER #############
plt = gl.GLScatterPlotItem(pos=p, color=C, size=10, pxMode=False)
w.addItem(plt)

g=gl.GLGridItem()
g.setSize(100,100,100)
w.addItem(g)

# show
w.show()
pg.QtGui.QApplication.exec_()
