import numpy as np
import imutils
import cv2


class SingleMotionDetector:

	def __init__(self, accumWeight=0.5):
		self.accumWeight = accumWeight
		self.bg = None

	def update(self, newImg):
		if self.bg is None:
			self.bg = newImg.copy().astype("float")
			return
		# update background model - accumulating the weighted average
		cv2.accumulateWeighted(newImg, self.bg, self.accumWeight)

	def detect(self, newImg, noise=25, upperThreshold=255):
		# absolute difference between background model and newest image 
		absDiff  = cv2.absdiff(self.bg.astype("uint8"), newImg)
		# threshold the delta image
		thresh = cv2.threshold(absDiff, noise, upperThreshold, cv2.THRESH_BINARY)[1]
		# perform erosions and dilations to remove small blobs
		thresh = cv2.erode(thresh,  None, iterations=2)
		thresh = cv2.dilate(thresh, None, iterations=2)

		# find contours in the thresholded image
		contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		contours = imutils.grab_contours(contours)

		# initialize minimum - maximum bounding box regions for motion
		(minX, minY) = ( np.inf,  np.inf)
		(maxX, maxY) = (-np.inf, -np.inf)

		if len(contours) == 0:
			return None
		# loop over the contours
		for c in contours:
			# compute bounding box of the contour 
			# => update the minimum and maximum bounding box regions
			(x, y, w, h) = cv2.boundingRect(c)
			(minX, minY) = ( min(minX, (x + 0)), min(minY, (y + 0)) )
			(maxX, maxY) = ( max(maxX, (x + w)), max(maxY, (y + h)) )
		
		# return tuple of thresholded image - along with bounding box
		return (thresh, (minX, minY, maxX, maxY))
