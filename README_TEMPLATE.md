# claude-code-template

This is a generic git project to support the Claude Code Assistant.

## What is it about?

This project offers a safe-setup to allow all permissions to Claude Code inside a secured environment. This environment knows no API keys or your credentials to ensure that the changes are limited to the workspace.

The tasks requested to Claude Code are define in `.claude/tasks` under the form of Markdown files.

## How to create a project with this template?

Start by cloning the latest version of this repository:

```
git clone --depth 1 https://github.com/medispring/claude-code-template my-project
cd my-project
```

Remove old git history and rename this README.md:

```
rm -rf .git
mv README.md README_TEMPLATE.md
touch README.md
```

Re-initialize as a brand-new repository:

```
git init
git add .
git commit -m "Initial commit"
```

**Optional** : Add a remote if required:

```
git branch -M main
git remote add origin <remote>
git push -u origin main
```

## How to use this template?

- Ensure that Docker, Git and Make are installed on your environment.

```
git --version
make --version
docker --version
```

- Edit `CLAUDE.md` and complete the <ADD XXX> (project purpose, description, design principles...)
- Update the `.claude/safe-setup` environment
  - In `docker-compose.yml`, update the `image` and the `container_name`
  - Create `.env` file based on `.env.example` and populate the correct parameters.
  - In `Dockerfile.claude`, uncomment the language you would like to use.
- Run the safe setup container to ensure that everything is fine:

```
cd .claude/safe-setup
make up
make claude
```

- At the first start, you will need to add a Claude Code API key.
- Select the model Opus with the command: `/model`
- Install plugins if required: `/plugin`
- Ask Claude to know the rules: `read the CLAUDE.md file`
- You are good to go!

## Your first Claude task

- In `.claude/tasks/todo`, add your first task. Example : `0000-start.md`. Inside the Markdown file, describe the problem you want to solve and potentially explain idea of implementation.
- In the Claude safe-setup container, ask Claude : `implement next task`
- When everything is fine, the task goes from `todo` to `done``
- Validate the changes in your IDE based on the latest local git commit.
- Push if you are fine.
- Go with next task.
