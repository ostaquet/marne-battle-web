# Problem to solve

The virtual environment for Python is generated with the `scripts/venv.sh`. It works well and create a virtual environment in `venv/`.

However, when Claude Code is using the script to initialize the environment (in Docker container), it brakes my environment (on my MacBook).

Therefore, the directory for the virtual environment should be different for the Docker container and my environment.

The script should generate a virtual environment in `venv_docker/` for the Docker container and `venv_local/` for my local environment. The scripts `script/lint.sh` and `scripts/test.sh` should also be adapted.
