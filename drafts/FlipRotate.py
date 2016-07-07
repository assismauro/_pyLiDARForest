import numpy as np
import cv2

img=cv2.imread(r'h:\transects\img\NP_T-054.jpg')
rimg=img.copy()
fimg=img.copy()
rimg=cv2.flip(img,1)
cv2.imwrite(r'h:\transects\img\NP_T-054r.jpg',rimg, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
fimg=cv2.flip(rimg,0)
cv2.imwrite(r'h:\transects\img\NP_T-054f.jpg',fimg, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
