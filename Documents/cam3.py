import numpy as np
import cv2
# from matplotlib import pyplot as plt


img = cv2.imread('grab.jpg')

gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
