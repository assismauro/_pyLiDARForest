from laspy import file
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pyqtgraph.Qt import QtCore, QtGui

#las = file.File(r'H:\TRANSECTS\T_054\NP_T-054_FWF_LAS\NP_T-054_FWF.LAS')
las = file.File(r'D:\CCST\Software\img2lidar\img\fundo.las')

### something to graph ######

import numpy as np
'''
pi=3.1415
X=linspace(-10,10,100)
Y1=2+sin(X)
Y2=-2+Y1*Y1
Y3=cos(1*Y1)/(X+0.0131415)
Y4=4+sin(X)*cos(2*X)
Y=X
Z=exp(-0.1*X*X)*cos(0.3*(X.reshape(100,1)**2+X.reshape(1,100)**2))

'''
X=las.X[0:10]-np.amin(las.X[0:10])
Y=las.Y[0:10]-np.amin(las.Y[0:10])
Z=las.Z[0:10]-np.amin(las.Z[0:10])               #            DISTANCE!!!!

#data=np.column_stack((np.column_stack((X,Y)),Z))

data=np.column_stack((X,Y))

#pg.plot(data)

'''
#Z=np.random.randint(0,10,size=(10,10))

##### plot 3D surface data  ####

app = QtGui.QApplication([])
w = gl.GLViewWidget()
w.opts['distance'] = 20
w.show()
w.setWindowTitle('pyqtgraph example: GLScatterPlotItem')
  
g = gl.GLGridItem()
w.addItem(g)
w = gl.GLViewWidget()
## Saddle example with x and y specified

p = gl.GLScatterPlotItem(pos=data,size=6.0,color=(0.0, 1.0, 0.0, 0.5),pxMode=False) #, shader='heightColor'
w.addItem(p)
# show
w.show()
pg.QtGui.QApplication.exec_()
'''