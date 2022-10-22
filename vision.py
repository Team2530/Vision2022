import threading
import cv2
import numpy as np
import sys, re, subprocess, time

from streaming import FlaskImageStreamer

CAM_RXP = re.compile(r'(.+) .+:\n\t(.+)')

# Finds the (/dev/videoX) device file of all cameras with a name including `camname`
def find_cameras(camname):
    output = subprocess.run(['v4l2-ctl', '--list-devices'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    devices = {k:v for k,v in CAM_RXP.findall(output)}
    cams = {k:v for k,v in devices.items() if camname in k}
    return list(cams.values())

cam1 = cv2.VideoCapture(find_cameras("LifeCam")[0], cv2.CAP_V4L2) if sys.platform == 'linux' else cv2.VideoCapture(1, cv2.CAP_DSHOW)

stream = FlaskImageStreamer()
th = threading.Thread(target=stream.run_server, daemon=True)
th.start()

if not cam1.isOpened():
    print("Error opening camera")
    exit(1)

while (True):
    try:
        time.sleep(1/60)
        ret, frame = cam1.read()
        
        # cv2.imshow("Test", frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
            # break
            
        small_frame = cv2.resize(frame, (720, 480))
        stream.update(small_frame)
    except KeyboardInterrupt:
        break;

# Cleanup
cam1.release()
cv2.destroyAllWindows()
