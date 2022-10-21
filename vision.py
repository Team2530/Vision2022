import cv2
import numpy as np

cam1 = cv2.VideoCapture(0, cv2.CAP_DSHOW)

while (True):
    ret, frame = cam1.read()

    cv2.imshow("Test", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cam1.release()
cv2.destroyAllWindows()
