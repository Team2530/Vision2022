import cv2
import numpy as np
import sys

cam1 = cv2.VideoCapture("/dev/video6", cv2.CAP_V4L2) if sys.platform == 'linux' else cv2.VideoCapture(1, cv2.CAP_DSHOW)

if not cam1.isOpened():
    print("Error opening camera")
    exit(1)

while (True):
    ret, frame = cam1.read()
    
    cv2.imshow("Test", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cam1.release()
cv2.destroyAllWindows()
