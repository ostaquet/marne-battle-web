#!/bin/bash

# Configure git user/email from environment variables if provided
if [ -n "$GIT_USER_NAME" ]; then
    git config --global user.name "$GIT_USER_NAME"
fi

if [ -n "$GIT_USER_EMAIL" ]; then
    git config --global user.email "$GIT_USER_EMAIL"
fi

# Ensure that the Docker socket has the correct permissions for the 'docker' group
# (to let Claude run integration tests in his own environment)
sudo chown root:docker /var/run/docker.sock

# Execute the command passed to the container
exec "$@"
