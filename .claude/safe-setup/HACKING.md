# Hacking with Claude Code

This Docker setup provides a sandboxed environment with all tools needed to hack on the project.

- Claude Code CLI

## Prerequisites

1. Docker and Docker Compose installed
2. A Claude Code account

## Getting started

```
# Build and start containers
make up

# Enter the dev environment with skip all permissions
make claude
```

You're now user `claude` in `/workspace` (the project root).

## Persistent Data

- **Claude history**: Stored in a named Docker volume (`claude-history`) that persists across container restarts
- **Git configuration**: Automatically set from `GIT_USER_NAME` and `GIT_USER_EMAIL` environment variables

## Commands

| Command        | Description                  |
| -------------- | ---------------------------- |
| `make up`      | Build and start containers   |
| `make down`    | Stop containers              |
| `make shell`   | Enter dev container          |
| `make restart` | Restart everything           |
| `make logs`    | Follow container logs        |
| `make ps`      | Show container status        |
| `make clean`   | Remove containers and images |
| `make claude`  | Directly launch claude       |
