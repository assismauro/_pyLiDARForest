import cv2
import numpy as np
image = np.zeros(shape=(20000,5000), dtype = "uint8")
print(cv2.imwrite(r"d:\teste.png",image))
raw_input('x')