from flask import Response
from flask import Flask
from flask import render_template
import time
import cv2

class FlaskImageStreamer():
    def __init__(self) -> None:
        self.app = Flask(__name__)
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
        self.app.run(host, port, threaded=True)

    