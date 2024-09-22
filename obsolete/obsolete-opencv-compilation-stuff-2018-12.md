# OpenCV 4 on Raspian Stretch

<www.pyimagesearch.com/2015/02/23/install-opencv-and-python-on-your-raspberry-pi-2-and-b/>
<www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/>
<www.pyimagesearch.com/2016/01/04/unifying-picamera-and-cv2-videocapture-into-a-single-class-with-opencv/>

## OpenCV 4 on Raspian Stretch - 2

www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/

### IlmThread error (openexr ?)

```bash
#        ./../lib/libopencv_imgcodecs.so.4.0.0: undefined reference to `IlmThread::TaskGroup::TaskGroup()' undefined reference IlmThread TaskGroup

sudo apt-get install exrtools
sudo apt-get install libilmbase-dev
sudo apt-get install libilmbase12

sudo apt-get install libopenexr22
sudo apt-get install openimageio-tools  python-openimageio

sudo apt-get install libv4l-dev
```

#### From the cmake output

sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev
<!-- sudo apt-get install libdc1394-2 libdc1394 libavresample tesseract lept -->

cd ~/.virtualenvs/cv/lib/python3.5/site-packages/

ln -s /usr/local/python/cv2/                                                  cv2
ln -s /usr/local/python/cv2/python-3.5/cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so

## Tutorials from OpenCV

Software setup of the  Pi Camera
www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/

All the tutorials
www.pyimagesearch.com/practical-python-opencv/?src=pi-opencv-install

Motion detection
www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/

docs.opencv.org/master/db/deb/tutorial_display_image.html

opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_feature2d/py_shi_tomasi/py_shi_tomasi.html

