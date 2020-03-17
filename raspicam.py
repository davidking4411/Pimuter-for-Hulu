from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import imutils
import cv2
import numpy as np
import xmltodict
import requests

def get_active_app():
    response = requests.get('http://192.168.1.20:8060/query/active-app')
    response_dict = xmltodict.parse(response.text)
    try: #if on home screen 'app' is last field so it'll error out
        return response_dict['active-app']['app']['#text']
    except:
        return 'Home'

# initialize the camera and grab a reference to the raw camera capture
ad_history = [0,0,0,0]
#lower_green = np.array([20, 50,48]) # HSV values
#upper_green = np.array([50, 260, 255])
green = np.uint8([[[49, 166, 187]]]) # GRB
hsvGreen = cv2.cvtColor(green,cv2.COLOR_BGR2HSV)
lower_green = np.uint8([hsvGreen[0][0][0]-10,50,48])
upper_green = np.uint8([hsvGreen[0][0][0]+10,255,255])
lower_green = np.uint8([hsvGreen[0][0][0]-10,50,50])
upper_green = np.uint8([hsvGreen[0][0][0]+10,255,255])

#for rectangle
start_point = (int(640/2-75), int(480/2-70)) 
end_point = (int(640/2+75), int(480/2+70)) 
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
active_app = get_active_app()
try:
    requests.post('http://192.168.1.20:8060/keypress/VolumeUp')
    requests.post('http://192.168.1.20:8060/keypress/VolumeDown')
    
    
except KeyboardInterrupt:
    print('unmuting failed')

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array

    image = rawCapture.array
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    cropped_mask = mask[245:395,170:310]
    image_w_rec = cv2.rectangle(image, start_point, end_point, color, thickness)
    cv2.imshow('mask',mask)
    cv2.imshow('image',image_w_rec)
    sum_mask = sum(sum(cropped_mask))
    ad_history.pop(0)
    ad_history.append(sum_mask)
    print('history mean', np.mean(ad_history))
    if 10000 <= np.mean(ad_history) and np.mean(ad_history) <=13500:
           print('ad: '+ str(sum_mask))
           if not muted and active_app == 'Hulu':
               print('muting')
               requests.post('http://192.168.1.20:8060/keypress/VolumeUp')
               requests.post('http://192.168.1.20:8060/keypress/VolumeDown')
               requests.post('http://192.168.1.20:8060/keypress/VolumeMute')
               muted = True
    elif muted and (8000 >= np.mean(ad_history)):
           print('not ad: '+ str(sum_mask))
           print('unmuting')
           muted = False
           requests.post('http://192.168.1.20:8060/keypress/VolumeUp')
           requests.post('http://192.168.1.20:8060/keypress/VolumeDown')
    else:
           print('not ad: '+ str(sum_mask))


    if time.time()-check_time > 60*2: # check if Hulu is even the running app
        active_app = get_active_app()
        while active_app != 'Hulu':
            #don't bother getting another frame from the camera if Hulu isn't the current app
            print('waiting for Hulu app to start')
            time.sleep(60*3)
            active_app = get_active_app()

    key = cv2.waitKey(1)
    rawCapture.truncate(0)
    if key == 27: # esacpe key
        break

cv2.destroyAllWindows()