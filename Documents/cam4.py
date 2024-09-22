import time
import sys
import subprocess
# import ftputil
import cv2
import dropbox
import datetime
import imutils

from matplotlib import pyplot as plt
import numpy as np

from pyimagesearch.tempimage import TempImage

""" 
www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/
www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/

Use 
	ls /dev/video*
to check for cam and index

"""

# This does not work:
# res = subprocess.Popen(["sudo", "ls", "~/../../dev/video*"],shell=False, stdout=subprocess.PIPE, cwd=".")
# print(str(res))

conf = {
	"use_dropbox": True,
	"dropbox_access_token": "9YyWdwaEihAAAAAAAAAAED6LVes-nOVrPdza0Rk0pLkqEWu2J9sPJykgHEkOZ7q0",
	"dropbox_base_path": "raspberry",

	"show_video": True,
	"min_upload_seconds": 3.0,
	"min_motion_frames": 8,
	"camera_warmup_time": 2.5,
	"delta_thresh": 5,
	"resolution": [640, 480],
	"fps": 16,
	"min_area": 5000
}

if conf["use_dropbox"]:
	client = dropbox.Dropbox(conf["dropbox_access_token"])
	print("[SUCCESS] dropbox account linked")



cap = None
milliSecs = 0  # zero would be forever
milliSecs = 400

ext = ".jpg"

fadingAverage = None
recentMovement = False
motionCounter = 0
lastUploaded = datetime.datetime.now()


try:
	cap = cv2.VideoCapture()
	print("VideoCapture startet")


	# cam.open(1)
	# cam.open(-1)
	cap.open(0)
	print("[INFO] cam opened")
	print("[INFO] cam warming up...")
	time.sleep(conf["camera_warmup_time"])


	# if False:
	#	 piCap = PiCamera()
	#	 piCap.resolution = tuple(conf["resolution"])
	#	 piCap.framerate = conf["fps"]
	#	 piCamRawCapture = PiRGBArray(piCap, size=tuple(conf["resolution"]))
	#	 for f in piCap.capture_continuous(piCamRawCapture, format="bgr", use_video_port=True):
	#		 frame = f.array  # grab the raw NumPy


	if False:
		cap.set(cv2.CAP_PROP_FPS, 15)		   # seems unsupported for usb cam
		cap.set(cv2.CAP_PROP_FRAME_WIDTH, 240)  # seems unsupported for usb cam
		frameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)  # always returns -1.0

	fps, width, height = cap.get(cv2.CAP_PROP_FPS), cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	print("FPS %s - Width %d Height %d" % (str(fps), int(width), int(height)))
	
	
	for feat in range(0,11):

		timestamp = datetime.datetime.now()
		ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p") # string

		#call("streamer -q -f jpeg -s 640x480 -o ./current.jpeg", shell=True)
		#time.sleep(0.2);
		#call("killall -q streamer", shell=True)
		ok, imgOrig = cap.read()
		print("Reading result was %s" % str(ok))
		if ok:
			fileName = "current%d" % feat
			cv2.imwrite(fileName + ext, imgOrig)
			print("\tResult to file %s" % fileName + ext)
		else:
			break

		key = input("Press c or q...   ")
		if key == "c":
			pass
			# print("continue...")
		if key == "q":
			raise Exception("interrupted by 'q'")
		
		img = cv2.imread(fileName + ext)
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # gray

		img = imutils.resize(img, width=320) # smaller
		img = cv2.GaussianBlur(img, (21, 21), 0)  # blur it

		print("img grayscaled and blurred")
		features = cv2.goodFeaturesToTrack(img, 25, 0.01, 10)
		if features is not  None:
			# print(features)
			print("iterating features...")
			for feat in features:
				x, y = feat.ravel()
				cv2.circle(img, (x, y), 3, 255, -1)
		else:
			print("no features; possibly too dark...")


		print("Features marked with circles")		

		cv2.imwrite(fileName + "_grayscaled_features_to_track" + ext, img)

		if fadingAverage is None:
			print("[INFO] starting background model...")
			fadingAverage = img.copy().astype("float")
			# piCamRawCapture.truncate(0)
			continue
		
		# accumulate current frame to weighted average of previous frames...
		cv2.accumulateWeighted(img, fadingAverage, 0.5)
		# compute difference between current frame and running average
		# thus getting a 'trail of movement' like camera picture taken in the dark
		# while everything else remains dark 
		deltaToFadingAvg = cv2.absdiff(img, cv2.convertScaleAbs(fadingAverage))

		# threshold frameDelta image ("abstufen")
		thresh = cv2.threshold(deltaToFadingAvg, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]
		# dilate (widen) the thresholded image (fill small holes)
		thresh = cv2.dilate(thresh, None, iterations=2)
		# find contours on thresholded image
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)

		# loop over the contours
		for c in cnts:
			# if the contour is too small, ignore it
			if cv2.contourArea(c) < conf["min_area"]:
				continue

			(x, y, w, h) = cv2.boundingRect(c)  # compute the bounding box for the contour
			cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # draw it on img
			recentMovement = True

		# draw the text and timestamp on the frame
		# cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		# cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

		if recentMovement:
			motionCounter += 1
			if motionCounter >= conf["min_motion_frames"]:
				# enough continuous motions
				if (timestamp - lastUploaded).seconds >= conf["min_upload_seconds"]:
                    # long enough ago
					if conf["use_dropbox"]:
						t = TempImage()
						cv2.imwrite(t.path, img)
						print("\tabout to upload - %s" % ts)
						path = "/%s/%s.jpg" % ( conf["dropbox_base_path"], ts)
						client.files_upload(open(t.path, "rb").read(), path)
						t.cleanup()
				lastUploaded = timestamp
				motionCounter = 0 # reset motion counter
		else:
			# not enough continuous motions or room not occupied
			motionCounter = 0


		if False and conf["show_video"]:
			# display continuous flow?
			cv2.imshow("Security Feed", imgOrig)
			key = cv2.waitKey(1) & 0xFF
			if key == ord("q"):
				break


		# clear the stream in preparation for the next frame
		# piCamRawCapture.truncate(0)


		# plt.imshow(img), plt.show()

		# for cycle in range(0,1000):
		#	 # time.sleep(0.1)
		#	 key = cv2.waitKey(milliSecs)

		#	 if key != -1:
		#		 print('You pressed %d (0x%x), 2LSB: %d (%s)' % (key, key, key % 2**16,
		#														 repr(chr(key % 256)) if key % 256 < 128 else '?'))
		#	 else:
		#		 print(".", end='')
		#	 if key % 256 ==  99 or key == ord("c"):
		#			 continue
		#	 if key % 256 == 112 or key == ord("q"):
		#			 raise("interrupted by 'q'")

		# host = ftputil.FTPHost()
		# host.remove("/domains/public_html/webcam.jpg")
		# host.upload("./current.jpeg", "/domains/public_html/webc")
		# host.close()

except Exception as e:
	print("Exception main:")
	print(e)
finally:
	cap.release()
	cap = None
	cv2.destroyAllWindows()


