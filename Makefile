PYTHON_NAME=python3.8

REMOTE_IP=192.168.50.166
REMOTE_USER=odroid
REMOTE_SSH=${REMOTE_USER}@${REMOTE_IP}
SSH_IDENTITY=-i ~/.ssh/vision_id

test: deploy start_remote

# Copy to remote with git push over ssh
deploy:


# runs `starter` on the remote
start_remote:

# (re)starts a service on the remote to run the vision code
starter:

# Initializes deployment to the remote and venv on the remote (installs neccesary packages)
# Pubkey-based ssh authentication must be set up and set to be the default for REMOTE_USER@REMOTE_IP
setup:
	git remote add deployment ${REMOTE_SSH}