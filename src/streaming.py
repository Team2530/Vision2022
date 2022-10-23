from asyncio import subprocess
from re import L
import threading
from flask import Response
from flask import Flask
from flask import render_template
import shlex
import cv2
from flask_compress import Compress


class CameraVideoStreamer():
    def __init__(self, cam, width=720, height=480) -> None:
        self.cap = cv2.VideoCapture(*cam)
        self.cap.set(cv2.CAP_PROP_FOURCC,
                     cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        (self.grab, self.frame) = self.cap.read()
        self.stopped = False
        self.fresh = True

    def reader(self):
        while True:
            (self.grab, self.frame) = self.cap.read()
            self.fresh = True
            if (self.stopped):
                return

    def start(self):
        # start the thread to read frames from the video stream
        threading.Thread(target=self.reader, daemon=True).start()
        return self

    def stop(self):
        self.stopped = True

    def get_frame(self):
        self.fresh = False
        return self.frame


class FlaskMJPEGImageStreamer():
    def __init__(self) -> None:
        self.app = Flask(__name__)
        self.compress = Compress()
        self.last_frame = None
        self.stale = True

        pass

    def generate_image(self):
        while True:
            # Wait for a new frame
            # while not self.stale:
            #     time.sleep(1/60)
            self.stale = True
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + cv2.imencode('.jpg', self.last_frame)[1].tobytes() + b'\r\n')

    def respond(self):
        print("respond!")
        return Response(self.generate_image(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def update(self, img):
        self.last_frame = img
        # print("got a frame from the camera")
        self.stale = False

    def run_server(self, host='0.0.0.0', port=5000):
        self.app.add_url_rule('/', view_func=self.respond)
        self.compress.init_app(self.app)
        self.app.run(host, port, threaded=True)

    def release(self):
        pass


# class CompressedImageStreamer():
#     def __init__(self, width=720, height=480, bitrate=1024) -> None:
#         self.width = width
#         self.height = height
#         self.bitrate = bitrate
#         self.args = f'ffmpeg -s {width}x{height} -f rawvideo -pixel_format bgr24 -r 5 -vcodec msmpeg4v2 -b:v 25k -an -f h263'
#         self.cmd = None

#     def update(self, img):
#         self.cmd.stdin.write(cv2.resize(
#             img, (self.width, self.height)).tobytes())

#     def run_server(self, host='0.0.0.0', port=5000):
#         args = self.args + f" udp://{host}:{port}"
#         self.cmd = subprocess.Popen(args, stdin=subprocess.PIPE)

#     def release(self):
#         pass
