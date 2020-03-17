from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import imutils
import cv2
import numpy as np
import xmltodict
import requests

# initialize the camera and grab a reference to the raw camera capture
ad_history = [0,0,0,0]
#lower_green = np.array([20, 50,48]) # HSV values
#upper_green = np.array([50, 260, 255])
green = np.uint8([[[49, 166, 187]]])
hsvGreen = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
lower_green = np.uint8([hsvGreen[0][0][0]-10,50,48])
upper_green = np.uint8([hsvGreen[0][0][0]+10,255,255])

#for rectangle
start_point = (int(640/2-75), int(480/2-75)) 
end_point = (int(640/2+75), int(480/2+75)) 
color = (0, 255, 0) 
thickness = 2

muted = False
check_time = time.time()
camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 30
camera.iso = 400
rawCapture = PiRGBArray(camera, size=(640, 480))
time.sleep(.25)
camera.exposure_mode = 'off'
camera.meter_mode = 'spot'

# # allow the camera to warmup
# time.sleep(0.1)
# # grab an image from the camera
# camera.capture(rawCapture, format="bgr")
# image = rawCapture.array
# #image = cv2.imread('foo.jpg')
# hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
# mask = cv2.inRange(hsv, lower_green, upper_green)
# print(sum(sum(mask)))
# # cv2.imshow('a',image)
# # cv2.waitKey(0)
# # cv2.imshow('a',mask)
# # cv2.waitKey(0)

try:
    requests.post('http://192.168.1.20:8060/keypress/VolumeUp')
    requests.post('http://192.168.1.20:8060/keypress/VolumeDown')
    response = requests.get('http://192.168.1.20:8060/query/active-app')
    response_dict = xmltodict.parse(response.text)
    response_dict['active-app']['app']['#text']
except KeyboardInterrupt:
    print('unmuting failed')

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    #rawCapture = PiRGBArray(camera)
    #time.sleep(.5)
    #camera.capture(rawCapture, format='bgr')
    image = rawCapture.array
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    cropped_mask = mask[75:220,220:415]
    image_w_rec = cv2.rectangle(image, start_point, end_point, color, thickness)
    cv2.imshow('mask',mask)
    cv2.imshow('image',image_w_rec)
    sum_mask = sum(sum(cropped_mask))
    ad_history.pop(0)
    ad_history.append(sum_mask)
    print('history mean', np.mean(ad_history))
    if (26000 <= np.mean(ad_history)) and (np.mean(ad_history) <= 32000):
           print('ad: '+ str(sum_mask))
           if not muted and response_dict['active-app']['app']['#text'] == 'Hulu':
               print('muting')
               requests.post('http://192.168.1.20:8060/keypress/VolumeUp')
               requests.post('http://192.168.1.20:8060/keypress/VolumeDown')
               requests.post('http://192.168.1.20:8060/keypress/VolumeMute')
               muted = True
    elif muted and ((25000 >= np.mean(ad_history)) or (np.mean(ad_history) >= 33000)):
           print('not ad: '+ str(sum_mask))
           print('unmuting')
           muted = False
           requests.post('http://192.168.1.20:8060/keypress/VolumeUp')
           requests.post('http://192.168.1.20:8060/keypress/VolumeDown')
    else:
           print('not ad: '+ str(sum_mask))


    if time.time()-check_time > 60*5:
        response = requests.get('http://192.168.1.20:8060/query/active-app')
        response_dict = xmltodict.parse(response.text)
    
    key = cv2.waitKey(1)
    rawCapture.truncate(0)
    if key == 27:
        break

cv2.destroyAllWindows()