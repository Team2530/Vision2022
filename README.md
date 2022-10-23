# OpenCV vision on a ODROID-XU4

Prototype/template for future vision processing on a FRC robot.

## Requirements

Required APT packages:

- v4l2-utils
- PACKAGES REQUIRED ON REMOTE
- git
- python3.10
- python3.10-venv
- python3-opencv
- python3-tk
- python3-numpy

Python packages:

- OpenCV (installed via apt, enable global site-packages in venv)
- Numpy ^
- imutils
- flask_compress
- pupil_apriltags (windows) or dt_apriltags (linux)

Key-based SSH authentication must be set up and default for the remote ODROID

## TODOs

- [x] Automatic selection of correct camera(s) on linux using `v4l2-utils`
- [x] Network-streamed debug & overlay output from pipeline
- [x] Deployment & debug without committing (rsync current unstaged working directory instead of cloning?)
  - Seperate makefile command to push to the remote repo
  - Also need a command to push to all remotes (github and remote bare repo)
- [x] Systemd service to run script
  - [x] Makefile command to print debug output from systemd service (for debugging)
- [x] Proper apriltag library for linux
- [x] Network tables data output