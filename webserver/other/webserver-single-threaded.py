import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
import time
import traceback

# https://docs.python.org/3.7/library/http.server.html
class MyHandler(BaseHTTPRequestHandler):

	def do_GET(self):   # GET

		try:
			print("serving %s" % self.path)
			self.send_response(200)  # Send response status code


			# Root responsse
			if self.path == "/" or self.path == "":
				self.send_header('Content-type', 'text/html;charset=utf-8')
				self.end_headers()
				message = "pbu's raspberry pi says <b>hello</b><br>\n"
				self.wfile.write(bytes(message, "utf8"))
				message = "<a href='/video/'>Stream video</a><br>\n"
				self.wfile.write(bytes(message, "utf8"))
				return


			# non root urls
			p = self.path
			if p[:1] == "/":  # cleanse leading slash
				p = p[1:]
			# print("new path is %s" % (p))

			if p == "favicon.ico":
				self.send_response(404)
				self.end_headers()
				return


			if p.startswith("video/"):
				print("video/")

				try:
					import cv2
					from imutils.video import VideoStream
				except Exception as e:
					self.wfile.write(bytes("could not import cv2 or imutils<br>\n", "utf-8"))
					s = traceback.format_exc()
					self.wfile.write(bytes(s, "utf-8"))
					return

				import threading
				import imutils
				import io
				buf = io.BytesIO()
				# self.wfile.write(bytes("imports complete<br>\n", "utf-8"))
				print("imports complete")

				# core objects
				outputFrame = None
				lock = threading.Lock()
				vs = VideoStream(usePiCamera=1).start()
				# vs = VideoStream(src=0).start()
				time.sleep(0.9)

				# loop over frames from the video stream
				# self.wfile.write(bytes("stream starting<br>\n", "utf-8"))
				print("stream starting")
				self.wfile.write(b'HTTP/1.1 200 OK\r\n')  # self.send_response(200) not effective, since we never call self.end_headers()
				self.wfile.write(b'Content-Type: multipart/x-mixed-replace; boundary=frame\r\n') # setup continuous stream
				self.wfile.write(b'Content-Disposition: inline;filename=somefile.jpg\r\n') # chrome needs this
				self.wfile.write(b'\r\n') # end of headers major

				for idx, key in enumerate(range(1000000000)):
					frame = vs.read()
					frame = imutils.resize(frame, width=400)
					# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
					# gray = cv2.GaussianBlur(gray, (7, 7), 0)
					# grab the current timestamp and draw it on the frame
					# timestamp = datetime.datetime.now()
					# cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

					with lock:
						outputFrame = frame.copy()

					(flag, encodedImage) = cv2.imencode(".jpg", outputFrame) # encoded image is numpy.ndarray				
					if idx < 2 or (idx % 100) == 0:
						print("%4d frame to image %s" % (idx, str(flag)))

					# no send_header(), no end_headers(), instead explicitly self.wfile.write
					# self.send_header('Content-type', 'image/jpeg')
					# self.end_headers()


					self.wfile.write(b'--frame\r\n') # boundary from multipart/x-mixed-replace above
					self.wfile.write(b'Content-Type: image/jpeg\r\n')
					self.wfile.write(b'\r\n') # end of headers minor
					self.wfile.write(bytearray(encodedImage)) # next jpg image of the stream
					# self.wfile.write(b'\r\n') # another newline is not required

					if idx > 410:
						break

				# vs = VideoStream(usePiCamera=1).stop() # how do we release the cam?
				vs.stop()
				return

			#
			if p.startswith("file/"):
				print("file/")
				p = curdir + sep + p
				try:
					f = open(p)
				except Exception as e:
					s = traceback.format_exc()
					self.wfile.write(bytes(s, "utf-8"))
					return

				cnt = f.read()
				bCnt = bytes(cnt, "utf8")
				self.wfile.write(bCnt)
				f.close()
				return

		except Exception as e:
			print(traceback.format_exc())
			s = traceback.format_exc()
			self.wfile.write(bytes(s, "utf-8"))


try:
	print('about to start http server...')
	# the 127.0.0.1 constrains access to our webserver to our own computers
	ipPort = ('127.0.0.1', 8086)
	ipPort = ('', 80)
	httpd = HTTPServer(ipPort, MyHandler)
	print('			   http server started at %s...' % str(ipPort))

	buffer = 1
	sys.stderr = open('/var/log/webserver.log', 'w', buffer)

	httpd.serve_forever()  # break this with CTRL+Pause


except Exception as e:
	print(traceback.format_exc())
