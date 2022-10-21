PYTHON_NAME=python3.10
REMOTE_IP=192.168.50.166
REMOTE_USER=odroid
REMOTE_SSH=$(REMOTE_USER)@$(REMOTE_IP)
REMOTE_REMOTE_DIR=/home/$(REMOTE_USER)/vision.git
REMOTE_CLONE_DIR=/home/$(REMOTE_USER)/
REMOTE_VENV=vision_venv

SSH_IDENTITY=-i ~/.ssh/vision_id

test: deploy start_remote

# Copy to remote with git push over ssh
deploy:
	git push -u deployment master
	ssh $(REMOTE_SSH) -f 'cd $(REMOTE_CLONE_DIR)vision && git pull'

# runs `starter` on the remote
start_remote:

# (re)starts a service on the remote to run the vision code
starter:

# Initializes deployment to the remote and venv on the remote (installs neccesary packages)
# Pubkey-based ssh authentication must be set up and set to be the default for REMOTE_USER@REMOTE_IP
setup: remote_setup
	git remote add deployment $(REMOTE_SSH):$(REMOTE_REMOTE_DIR)
	git push -u deployment master
	
remote_setup:
	ssh $(REMOTE_SSH) -f 'mkdir -p $(REMOTE_REMOTE_DIR) && cd  $(REMOTE_REMOTE_DIR) && git --bare init; cd $(REMOTE_CLONE_DIR) && git clone $(REMOTE_REMOTE_DIR) && cd ./vision && $(PYTHON_NAME) -m venv $(REMOTE_VENV) && chmod +x ./$(REMOTE_VENV)/bin/activate'

remote_packages:
	ssh $(REMOTE_SSH) -f 'cd $(REMOTE_CLONE_DIR)vision && source ./$(REMOTE_VENV)/bin/activate'