import threading
from typing import List
import cv2
import numpy as np
import sys
import re
import subprocess
import time
from networktables import NetworkTables


if sys.platform == 'linux':
    import dt_apriltags as apriltags
else:
    import pupil_apriltags as apriltags

from streaming import CameraVideoStreamer, FlaskMJPEGImageStreamer

CAM_RXP = re.compile(r'(.+) .+:\n\t(.+)')

# Allow debugging with localhost robot simulator
NT_IP = "10.23.30.2" if sys.platform == 'linux' else "localhost"


# Finds the (/dev/videoX) device file of all cameras with a name including `camname`
def find_cameras(camname):
    output = subprocess.run(['v4l2-ctl', '--list-devices'],
                            stdout=subprocess.PIPE).stdout.decode('utf-8')
    devices = {k: v for k, v in CAM_RXP.findall(output)}
    cams = {k: v for k, v in devices.items() if camname in k}
    return list(cams.values())


# Draws apriltag detections as an overlay
def draw_tags(
    image,
    tags: List[apriltags.Detection],
):
    for tag in tags:
        tag_id = tag.tag_id
        center = tag.center
        corners = tag.corners

        center = (int(center[0]), int(center[1]))
        corner_01 = (int(corners[0][0]), int(corners[0][1]))
        corner_02 = (int(corners[1][0]), int(corners[1][1]))
        corner_03 = (int(corners[2][0]), int(corners[2][1]))
        corner_04 = (int(corners[3][0]), int(corners[3][1]))

        cv2.circle(image, (center[0], center[1]), 5, (0, 0, 255), 2)

        cv2.line(image, (corner_01[0], corner_01[1]),
                 (corner_02[0], corner_02[1]), (255, 0, 0), 2)
        cv2.line(image, (corner_02[0], corner_02[1]),
                 (corner_03[0], corner_03[1]), (255, 0, 0), 2)
        cv2.line(image, (corner_03[0], corner_03[1]),
                 (corner_04[0], corner_04[1]), (0, 255, 0), 2)
        cv2.line(image, (corner_04[0], corner_04[1]),
                 (corner_01[0], corner_01[1]), (0, 255, 0), 2)

        cv2.putText(image, str(tag_id), (center[0] - 10, center[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)

    return image


if __name__ == "__main__":
    if sys.platform == "linux":
        import systemd.daemon
        systemd.daemon.notify('READY=1')

    IMG_WIDTH = 480
    IMG_HEIGHT = 360

    NetworkTables.initialize(server=NT_IP)
    table = NetworkTables.getTable("LemonLight")
    smartdash = NetworkTables.getTable("SmartDashboard")

    # cam1 = cv2.VideoCapture(find_cameras("Logitech")[
    #                         0]) if sys.platform == 'linux' else cv2.VideoCapture(1, cv2.CAP_DSHOW)
    # cam1.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    # # cam1.set(cv2.CAP_PROP_FPS, 30)  # LifeCam only does 30fps
    # # cam1.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    cvs = CameraVideoStreamer(
        [find_cameras("LifeCam")[0]] if sys.platform == 'linux' else [1, cv2.CAP_DSHOW], width=IMG_WIDTH, height=IMG_HEIGHT).start()

    stream = FlaskMJPEGImageStreamer()
    th = threading.Thread(target=stream.run_server, daemon=True)
    th.start()

    CAM_PARAMS = (
        333.82/1.143,
        333.82/1.143,
        321.976520,
        248.1072
    )

    # Tag size (m)
    TAG_SIZE = 0.1

    at_detector = apriltags.Detector(
        families="tag36h11",
        nthreads=8,
        quad_decimate=1.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0
    )

    # if not cam1.isOpened():
    #     print("Error opening camera")
    #     exit(1)

    prevtime = 0
    while (True):
        try:
            frame = cvs.get_frame()   # (cvs.grab, cvs.frame)

            # Resize to reduce bandwidth
            # small_frame = cv2.resize(
            #     frame, (IMG_WIDTH, IMG_HEIGHT), interpolation=cv2.INTER_NEAREST)
            small_frame = frame

            debug_image = small_frame.copy()

            small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

            tags = at_detector.detect(
                small_frame,
                estimate_tag_pose=True,
                camera_params=CAM_PARAMS,
                tag_size=TAG_SIZE,
            )

            table.putNumber("targetsTracking", len(tags))
            table.putNumberArray(
                "centerX", [t.center[0] - IMG_WIDTH/2 for t in tags])
            table.putNumberArray(
                "centerY", [t.center[1] - IMG_WIDTH/2 for t in tags])
            table.putNumberArray("poseX", [t.pose_t[0]*2 for t in tags])
            table.putNumberArray("poseY", [t.pose_t[1]*2 for t in tags])
            table.putNumberArray("poseZ", [t.pose_t[2]*2 for t in tags])

            debug_image = draw_tags(debug_image, tags)

            stream.update(debug_image)

            now = time.time()
            fps = int(1/(now - prevtime))
            prevtime = now
            print(fps)
        except KeyboardInterrupt:
            break

    # Cleanup
    # cam1.release()
    cv2.destroyAllWindows()
    stream.release()
