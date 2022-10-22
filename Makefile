PYTHON_NAME=python3.10
REMOTE_IP=192.168.50.166
REMOTE_USER=odroid
REMOTE_SSH=$(REMOTE_USER)@$(REMOTE_IP)
REMOTE_REMOTE_DIR=/home/$(REMOTE_USER)/vision.git
REMOTE_CLONE_DIR=/home/$(REMOTE_USER)/
REMOTE_VENV=vision_venv
SSH_IDENTITY=-i ~/.ssh/vision_id
RSYNC_PATH=/c/MinGW/msys/1.0/bin/rsync.exe

test: deploy restart_service view

view:
	ssh $(REMOTE_SSH) -tt 'journalctl -f | grep $$(systemctl --user show --property MainPID --value vision)'

# Send a working copy of the current unstaged version to the remote via ssh copy
deploy:
	sh ./copyremote.sh $(REMOTE_SSH):$(REMOTE_CLONE_DIR)vision

# Copy to remote with git push over ssh
deploy_git:
	git push -u deployment master
	ssh $(REMOTE_SSH) -f 'cd $(REMOTE_CLONE_DIR)vision && git clean -f && git pull'

restart_service:
	ssh $(REMOTE_SSH) -f 'cd $(REMOTE_CLONE_DIR)vision && mkdir -p /home/$(REMOTE_USER)/.config/systemd/user/ && cp ./vision.service /home/$(REMOTE_USER)/.config/systemd/user/ && systemctl --user daemon-reload && systemctl --user restart vision'

# Initializes deployment to the remote and venv on the remote (installs neccesary packages)
# Pubkey-based ssh authentication must be set up and set to be the default for REMOTE_USER@REMOTE_IP
setup: remote_setup remote_git_setup
	git remote add deployment $(REMOTE_SSH):$(REMOTE_REMOTE_DIR)
	git push -u deployment master
	
remote_setup:
	ssh $(REMOTE_SSH) -f 'mkdir -p $(REMOTE_CLONE_DIR)vision && cd $(REMOTE_CLONE_DIR)vision && $(PYTHON_NAME) -m venv $(REMOTE_VENV) && chmod +x ./$(REMOTE_VENV)/bin/activate'

remote_git_setup:
	ssh $(REMOTE_SSH) -f 'mkdir -p $(REMOTE_REMOTE_DIR) && cd  $(REMOTE_REMOTE_DIR) && git --bare init; cd $(REMOTE_CLONE_DIR) && git clone $(REMOTE_REMOTE_DIR) && cd ./vision && $(PYTHON_NAME) -m venv $(REMOTE_VENV) && chmod +x ./$(REMOTE_VENV)/bin/activate'

remote_packages:
	ssh $(REMOTE_SSH) -f 'cd $(REMOTE_CLONE_DIR)vision && source ./$(REMOTE_VENV)/bin/activate'