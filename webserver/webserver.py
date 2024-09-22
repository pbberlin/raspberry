import sys

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import errno

from urllib.parse import urlparse
import mimetypes

from os import curdir, sep, environ
import time
import traceback
import threading
import io
import datetime
from subprocess import call, run, PIPE
import json


# import computer vision modules
try:
	import cv2
	from imutils.video import VideoStream
	import imutils
except Exception as e:
	print("could not import module 'cv2' or 'imutils'<br>\n")
	print(traceback.format_exc())


# DC motors and relais
import RPi.GPIO as GPIO

# https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
from singlemotiondetector import SingleMotionDetector


from dcmotordriver import allStop, combined
from servodriver   import rangeServo, pwmSet

print("importing cv modules success")


# global stuff
# ---------------------------------
globCam = None  # camera - if we could reach it
globVS = None   # video stream
globLock = threading.Lock()  # locking
globFrame = None

camThread = None
stopCamThr = False

""" 
globThrottle = 0.0   -> CPU: 140%-100% - load avg empty ~1.50        - load avg one stream ~2.4 peaks to 2.8
globThrottle = 0.04  -> CPU:  65%- 40% - load avg empty ~0.50        - load avg one stream ~0.9 peaks to 1.2 - creeps up to 1,4 - two stream ~1.0
globThrottle = 0.1   -> CPU:  40%- 20% - load avg empty ~0.40        - load avg one stream ~0.6 peaks to 1.2
globThrottle = 0.2   -> CPU:  30%- 17% - load avg empty ~0.28        - load avg one stream ~0.5 peaks to 0.7
"""
globFrameRate =  16  # default is 32
globThrottle = 0.04  # throttles the cam loop AND the request loop, preventing equal content frames being read and streamed; > 1/32

# different frame rates have no effect

# globFrameRate = 4
# globThrottle = 0.12

# globFrameRate = 64
# globThrottle = 0.02


globWidthHeight = (240, 160)  # cpu load same as (320,240)
globWidthHeight = (160, 120)  # cpu load same as (320,240)

globWidthHeight = (640, 480)  # CPU load for 3 streams - 1.7
globWidthHeight = (320, 240)  # CPU load for 3 streams - 0.9


# cam stuff
# ---------------------------------
def camLoopFunc(arg1, arg2):
	global globCam, globVS, globLock, globFrame
	global stopCamThr
	global globFrame, globWidthHeight

	try:
		""" 
		set camera fps to (if the device allows)
        set_camera_fps value=30
        
		set buffer queue size of frame capturing to
        buffer_queue_size value=100
        
		throttling the querying of frames to
        fps value=30
        
		setting frame_id
        frame_id value=webcam
        
		camera info loading, take care as it needs the file:/// at the start, eg. file:///$(find your_camera_package)/config/your_camera.yaml
        camera_info_url value=
        
        flip_horizontal value=false
        flip_vertical value=false

        visualize on an image_view window the stream generated
        visualize value=true
		"""
		try:
			print("cam: starting camera with %s %s" % globWidthHeight)
			
			vs = VideoStream(usePiCamera=1, resolution=globWidthHeight, framerate=globFrameRate)

			if False:
				# globCam = ???  # we cannot access the cam of the video stream
				globCam.framerate = globFrameRate # has no effect
				globCam.rotation = 20
				globCam.hflip = True
				globCam.vflip = True
				globCam.video_stabilization = 1
				globCam.annotate_background = 2
				globCam.annotate_frame_num = 3
				globCam.CAPTURE_TIMEOUT = 60  # seconds


			globVS = vs.start()  # PiCam
			# globVS.resolution = globWidthHeight

			# globVS = VideoStream(src=0).start() # USB cam
			print("cam: started  camera with %s %s" % globWidthHeight)

		except Exception as e:
			print("cam: Problems starting camera")
			print(traceback.format_exc())
			return

		# time.sleep(1.1)
		time.sleep(1.1)
		time.sleep(1.1)
		print("cam: cam init complete %s %s" % (arg1, arg2))

		# initialize motion detector
		md = SingleMotionDetector(accumWeight=0.1)

		for idx, key in enumerate(range(1000000000)):

			global globThrottle
			time.sleep(globThrottle)

			localFrame = globVS.read()
			localFrame = imutils.resize(localFrame, width=globWidthHeight[0])

			if True:
				gray = cv2.cvtColor(localFrame, cv2.COLOR_BGR2GRAY)
				gray = cv2.GaussianBlur(gray, (7, 7), 0)

				if idx > 2*globFrameRate:  # minimal background average
					motion = md.detect(gray)
					if motion is not None:
						(thresh, (minX, minY, maxX, maxY)) = motion  # unpack tuple
						# draw "motion area" on the output frame
						cv2.rectangle(localFrame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)

				md.update(gray)  # update motion detector background model

			# timestamp = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
			timestamp = datetime.datetime.now().strftime("%A %d %B  %I:%M:%S %p")
			cv2.putText(localFrame, timestamp, (4, localFrame.shape[0] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.51, (220, 160, 160), 2)

			# with globLock:
			# 	globFrame = localFrame.copy()
			globFrame = localFrame.copy()

			if idx == 0:
				print("cam: loop started")
			elif (idx % 10000) == 0:
				print("cam: loop %d" % idx)
			if stopCamThr:
				print("cam: stop")
				break

	except Exception as e:
		print("cam: Exception")
		print(traceback.format_exc())


def getFrame():
	global globFrame
	return globFrame

	# global globLock
	# with globLock:
	# 	copyPerRequest = globFrame.copy()
	# return copyPerRequest


def camCleanUp():
	global globCam, globVS, camThread, stopCamThr
	global camThread
	try:
		if globCam is not None:
			globCam.close()
			print("camCleanUp: camera closed")
		if globVS is not None:
			globVS.stop()
			print("camCleanUp: video stream stopped")
		if camThread is not None:
			# camThread.join()
			stopCamThr = True
			print("camCleanUp: thread will stop")
	except Exception as e:
		print(traceback.format_exc())

	print("camCleanUp: complete")


# webserver stuff
# ---------------------------------


# https://stackoverflow.com/questions/14088294/multithreaded-web-server-in-python
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

# https://docs.python.org/3.7/library/http.server.html


class MyHandler(BaseHTTPRequestHandler):

	color = 'AABBEE'

	""" __init__ and __del__ make the class unusable as webserver handler """

	def do_GET(self):

		pth = self.path
		# print("serving %s" % pth)
		query = urlparse(self.path).query
		paramsGet = {}
		if len(query) > 2:
			print("\tquery is %s" % query)
			paramsGet = dict(qc.split("=") for qc in query.split("&"))


		try:
			if pth == "/favicon.ico":
				try:
					f = open("./templates" + pth, 'rb')
					favCnt = f.read()
				except Exception as e:
					s = traceback.format_exc()
					self.wfile.write(bytes(s, "utf-8"))
					return
				self.send_response(200)
				self.send_header('Content-type', 'image/x-icon')
				self.end_headers()
				# self.wfile.write(bytes(favCnt, "utf8"))
				self.wfile.write(favCnt)
				f.close()
				return


			if pth.startswith("/templates/"):
				pth = "." + pth
				try:
					f = open(pth)
					fileCnt = f.read()
				except Exception as e:
					s = traceback.format_exc()
					self.wfile.write(bytes(s, "utf-8"))
					return
				mt = mimetypes.MimeTypes().guess_type(pth)[0]
				# print("mimetype for %s is %s" % (pth, mt))
				self.send_response(200)
				self.send_header('Content-type', mt)
				self.end_headers()
				self.wfile.write(bytes(fileCnt, "utf8"))
				f.close()
				return


			if pth == "/" or pth == "":
				self.send_response(200)
				self.send_header('Content-type', 'text/html;charset=utf-8')
				self.end_headers()
				with open('./templates/index.html', 'r') as tplFile:
					template = tplFile.read()
				document = template.format(color=self.color, content1="<h3>pbu's raspberry pi says <b>hello</b> </h3>", content2="")
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/htop/"):
				self.send_response(200)
				sProc = run(["sh", "/home/pi/webserver/htop2html.sh"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				# time.sleep(0.4)  # waiting is useless
				if sProc.returncode != 0 or sProc.stderr != "":
					self.send_header('Content-type', 'text/plain')
					self.end_headers()
					document = "RC%d - %s" % (sProc.returncode, sProc.stdout)
					document += "\terr %s" % (sProc.stderr)
				else:
					self.send_header('Content-type', 'text/html;charset=utf-8')
					self.end_headers()
					htopFile = open("/home/pi/webserver/dump-htop.html", "r")
					document = htopFile.read()
					search = ""
					replace = ""
					document = document.replace(search, replace, -1)
				self.wfile.write(bytes(document, "utf8"))
				sProc = run(["vcgencmd", "measure_temp"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				document = "<p>RC%d - Temperature %s</p>\n" % (sProc.returncode, sProc.stdout)
				if sProc.stderr != "":
					document += "\ttemperature error %s" % (sProc.stderr)
				self.wfile.write(bytes(document, "utf8"))
				self.wfile.write(bytes("<br> <a href='/'>Back </a>", "utf8"))
				return


			if pth.startswith("/log/"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html;charset=utf-8')
				self.end_headers()
				sProc = run(["/usr/bin/tail", "--lines=120", "/var/log/webserver.log"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				logCnt = "RC%d\n%s" % (sProc.returncode, sProc.stdout)
				if sProc.stderr != "":
					logCnt += "\terr %s" % (sProc.stderr)
				# self.wfile.write(bytes(logCnt, "utf8"))
				with open('./templates/index.html', 'r') as tplFile:
					template = tplFile.read()
				document = template.format(color=self.color, content1="<br>", content2="<pre>%s</pre>" % logCnt)
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/webserver-restart/"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html;charset=utf-8')
				# import urllib
				# url = urllib.request.urlopen(self).geturl()
				import socket
				url = "http://%s/" % socket.gethostname()
				print("Redirecting to %s" % url)
				self.send_header('Location', url)
				self.end_headers()
				self.wfile.write(bytes("<br><a accesskey='r' href='/'>Refresh after a second...</a><br>\n", "utf8"))
				self.wfile.flush()
				sProc = run(["sh", "/home/pi/webserver/rest.sh"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				document = "RC%d - %s" % (sProc.returncode, sProc.stdout)
				if sProc.stderr != "":
					document += "\terr %s" % (sProc.stderr)
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/webserver-stop/"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html;charset=utf-8')
				self.end_headers()
				self.wfile.write(bytes("<br><a accesskey='r' href='/'>Refresh after a second...</a>\n", "utf8"))
				self.wfile.flush()
				sProc = run(["sh", "/home/pi/webserver/stop.sh"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				document = "RC%d - %s" % (sProc.returncode, sProc.stdout)
				if sProc.stderr != "":
					document += "\terr %s" % (sProc.stderr)
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/shutdown/"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html;charset=utf-8')
				self.end_headers()
				self.wfile.write(bytes("<br><a accesskey='r' href='/'>Refresh after restart...</a>\n", "utf8"))
				self.wfile.flush()
				sProc = run(["sh", "/home/pi/webserver/shutdown.sh"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				document = "RC%d - %s" % (sProc.returncode, sProc.stdout)
				if sProc.stderr != "":
					document += "\terr %s" % (sProc.stderr)
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/ifconfig/"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html;charset=utf-8')
				self.end_headers()
				self.wfile.write(bytes("<br><a accesskey='h' href='/'>Return to homepage</a>\n", "utf8"))
				self.wfile.flush()
				sProc = run(["sh", "/home/pi/webserver/ifconfig.sh"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				document = "RC%d - %s" % (sProc.returncode, sProc.stdout)
				document = "<pre>" + document + "</pre>"
				if sProc.stderr != "":
					document += "\terr %s" % (sProc.stderr)
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/sleep"):
				self.send_response(200)
				self.send_header('Content-type', 'text/plain')
				self.end_headers()
				self.wfile.write(bytes("start... thread %s\n" % (threading.currentThread().getName()), "utf8"))
				time.sleep(8.9)
				self.wfile.write(bytes("after sleeping 8 seconds\n", "utf8"))
				return


			if pth.startswith("/relais-proc/"):
				self.send_response(200)
				self.end_headers()
				sProc = run(["sh", "/home/pi/webserver/sudo-python.sh", "/home/pi/webserver/relais-start.py"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				document = "RC%d - %s" % (sProc.returncode, sProc.stdout)
				if sProc.stderr != "":
					document += "\terr %s" % (sProc.stderr)
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/relais-on-off/"):
				self.send_response(200)
				self.end_headers()
				relaisGPIO = 22
				GPIO.setmode(GPIO.BCM)
				GPIO.setup(relaisGPIO, GPIO.OUT)
				if paramsGet["state"] == "on":
					GPIO.output(relaisGPIO, GPIO.HIGH)
					msg = "Relais switched on"
				if paramsGet["state"] == "off":
					GPIO.output(relaisGPIO, GPIO.LOW)
					msg = "Relais switched off"
				# time.sleep(0.1)
				# GPIO.cleanup() # at the end
				with open('./templates/index.html', 'r') as tplFile:
					template = tplFile.read()
				document = template.format(color=self.color, content1="<br>", content2=msg)
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/servo-proc/"):
				self.send_response(200)
				self.end_headers()
				# return_code = call(["sh", "/home/pi/webserver/sudo-python.sh", "/home/pi/Documents/servo-2-calibrate.py"])
				# print("return code was %d"  % return_code)
				sProc = run(["sh", "/home/pi/webserver/sudo-python.sh", "/home/pi/Documents/servo-2-calibrate.py"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				document = "RC%d - %s" % (sProc.returncode, sProc.stdout)
				if sProc.stderr != "":
					document += "\terr %s" % (sProc.stderr)
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/servo/"):
				self.send_response(200)
				self.end_headers()
				# servo pulse lengths
				minPos = int(0.029 * 4096)  # min pulse length - out of 4096
				neuPos0 = int(0.046 * 4096) - 90
				neuPos1 = int(0.046 * 4096)  # neutral pos
				maxPos = int(0.130 * 4096)  # max pos
				# run them
				pwmSet(0, neuPos0)
				time.sleep(0.8)
				rangeServo(0, neuPos0, maxPos, 28, 0.15)
				pwmSet(0, 300)
				rangeServo(1, neuPos1, maxPos)
				with open('./templates/index.html', 'r') as tplFile:
					template = tplFile.read()
				document = template.format(color=self.color, content1="<br>", content2="Servos moved")
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/brush-proc/"):
				self.send_response(200)
				self.end_headers()
				sProc = run(["sh", "/home/pi/webserver/sudo-python.sh", "/home/pi/Documents/brush-4-gpiozero.py"], stdout=PIPE, stderr=PIPE, universal_newlines=True)
				document = "RC%d - %s" % (sProc.returncode, sProc.stdout)
				if sProc.stderr != "":
					document += "\terr %s" % (sProc.stderr)
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/brush/"):
				self.send_response(200)
				self.end_headers()
				msg = combined(0.6, +0.2)
				time.sleep(1.1)  
				msg = combined(0.6, -0.2)
				time.sleep(1.1)  
				allStop()
				with open('./templates/index.html', 'r') as tplFile:
					template = tplFile.read()
				document = template.format(color=self.color, content1="<br>", content2="DC engines moved")
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth.startswith("/video/"):
				buf = io.BytesIO()  # per request buf
				# self.send_response(200) not effective, since we never call self.end_headers()
				self.wfile.write(b'HTTP/1.1 200 OK\r\n')
				# setup continuous stream
				self.wfile.write(
					b'Content-Type: multipart/x-mixed-replace; boundary=frameboundary\r\n')
				# chrome needs this
				self.wfile.write(b'Content-Disposition: inline;filename=somefile.jpg\r\n')
				self.wfile.write(b'\r\n')  # end of headers major

				for idx, key in enumerate(range(1000000000)):

					requestFrame = getFrame()
					if requestFrame is None:
						print("getFrame() returned none - waiting")
						time.sleep(0.4)
						continue

					global globThrottle
					time.sleep(globThrottle)

					(flag, encodedImage) = cv2.imencode(
						".jpg", requestFrame)  # encoded image is numpy.ndarray
					if idx < 2 or (idx % 400) == 0:
						print("\trequest: %4d frame conv image: %s" % (idx, str(flag)))

					# no send_header(), no end_headers(), instead explicitly self.wfile.write
					# self.send_header('Content-type', 'image/jpeg')
					# self.end_headers()
					# boundary from multipart/x-mixed-replace above
					self.wfile.write(b'--frameboundary\r\n')
					self.wfile.write(b'Content-Type: image/jpeg\r\n')
					self.wfile.write(b'\r\n')  # end of headers minor
					self.wfile.write(bytearray(encodedImage))  # next jpg image of the stream
					# self.wfile.write(b'\r\n') # another newline is not required
					# if idx > 810:
					if idx > 111810:
						break
				return


			if pth.startswith("/video-window/"):
				self.send_response(200)
				self.send_header('Content-type', 'text/html;charset=utf-8')
				self.end_headers()

				cnt1 = '''
					<br>
					<img src='/video/' width='48%'  style='float: left;'  />
					<img src='/video/' width='48%'  style='float: left;'  />
				'''
				with open('./templates/index.html', 'r') as tplFile:
					template = tplFile.read()
				document = template.format(color=self.color, content1=cnt1, content2="")
				self.wfile.write(bytes(document, "utf8"))
				return


			if pth == "/drag.html":
				self.send_response(200)
				self.send_header('Content-type', 'text/html;charset=utf-8')
				self.end_headers()
				with open('./templates/drag.html', 'r') as tplFile:
					template = tplFile.read()
				document = template.format()
				self.wfile.write(bytes(document, "utf8"))
				return
			if pth == "/drag.js":
				self.send_response(200)
				self.send_header('Content-type', 'application/javascript')
				self.end_headers()
				with open('./templates/drag.js', 'r') as tplFile:
					template = tplFile.read()
				self.wfile.write(bytes(template, "utf8"))
				return




		except Exception as e:
			if e.errno == errno.EPIPE:
				print("\tbrowser closed for %s" % pth)
			else:
				print("exception executing %s" % pth)
				print(traceback.format_exc())
				s = traceback.format_exc()
				try:
					self.wfile.write(bytes(s, "utf-8"))
				except Exception as e:
					print("Could not write exception to website - broken pipe - see log...")
		finally:
			# print("\trequest %s finished" % pth)
			pass



	def do_POST(self):
		pth = self.path
		query = urlparse(self.path).query
		paramsGet = {}
		if len(query) > 2:
			print("\tquery is %s" % query)
			paramsGet = dict(qc.split("=") for qc in query.split("&"))
		if pth.startswith("/brush-ajax/"):
			self.send_response(200)
			self.send_header('Access-Control-Allow-Origin', '*')
			self.send_header('Content-type', 'application/json')
			self.end_headers()
			val1 = paramsGet["key1"]
			val2 = paramsGet["key2"]
			cl = int(paramsGet["content-length"])


			bodyString = self.rfile.read(cl)
			data = json.loads(bodyString)
			print(json.dumps(data, sort_keys=True, indent=4))

			cntrl = data["Control"]
			x = float(data["X"])
			y = float(data["Y"])
			# print("ctrl|x|y  %s|%f|%f" %(cntrl,x,y))
			if cntrl == "ctrl1":
				msg = combined(y,x)
				time.sleep(1.5) # still too afraid of continuous thrust
				allStop()

			# document = '{ "v1": "%s", "v2": "%s", "cl": %d, "Control": "%s" , "X": "%s" , "Y": "%s" }' % (val1, val2, cl, data["Control"], data["X"], data["Y"])
			document = json.dumps( {"msg": msg, "Y": data["Y"], "X": data["X"], "Control": data["Control"] }, sort_keys=False, indent=4)
			self.wfile.write(bytes(document, "utf8"))
			return







# webserver stuff
# ---------------------------------

try:
	print('starting http server...')
	ipPort = ('127.0.0.1', 8086)  # local access
	ipPort = ('', 80)
	# httpd = HTTPServer(ipPort, MyHandler) # single threaded
	server = ThreadedHTTPServer(ipPort, MyHandler)  # multi threaded
	print('\thttp server started at %s...' % str(ipPort))

	# all systemd log redirection options are *blocked*, because we need a *tty* for stdout
	logDir = '/var/log/webserver.log'
	buffer = 1
	logDirect = environ.get('LOG_DIRECT', 'log-to-file')
	if logDirect == 'log-to-file':
		print('\tRunning as service: Redirecting stdout/stderr to %s' % logDir)
		sys.stderr = open(logDir, 'w', buffer)
		sys.stdout = sys.stderr

	# global camThread # this already *is* global scope
	camThread = threading.Thread(target=camLoopFunc, args=["arg1-val", "arg2-val"])
	camThread.start()


	server.serve_forever()  # break this with CTRL+Pause


except Exception as e:
	print(traceback.format_exc())
finally:
	camCleanUp()
	try:
		GPIO.cleanup()
	except Exception as e:
		print("GPIO.cleanup() belched - since GPIO was never used")
