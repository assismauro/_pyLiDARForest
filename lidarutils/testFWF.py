import lasFWF
import numpy as np
import peakutils
from peakutils.plot import plot as pplot
from matplotlib import pyplot

'''
centers = (30.5, 72.3)
x = numpy.linspace(0, 120, 121)
y = (peakutils.gaussian(x, 5, centers[0], 3) +
    peakutils.gaussian(x, 7, centers[1], 10) +
    numpy.random.rand(x.size))
pyplot.figure(figsize=(10,6))
pyplot.plot(x, y)
pyplot.title("Data with noise")
pyplot.show()
'''

fwf=lasFWF.FWFFile(r'H:\TRANSECTS\T_054\NP_T-054_FWF_LAS\NP_T-054_FWF.LAS')

index=1000
y=fwf.GetFWFData(index)
x=np.linspace(0,len(y),len(y))
pyplot.figure(figsize=(10,6))
pyplot.plot(x, y)
pyplot.title("Full Waveform")
pyplot.show()


#data=fwf.GetFWFData(111)


#with open(r'E:\temp\test.csv', 'w+') as csv:
#    for i in range(0,999):
#        data=fwf.GetFWFData(i)
#        np.savetxt(csv,[data],fmt='%2d',delimiter=';',newline='\n')

fwf.close()