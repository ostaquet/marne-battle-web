# Claude Development Guide for <ADD PROJECT NAME>

This document providers instructions for AI assistants (like Claude) working on <ADD PROJECT NAME>.

## Project Overview

<ADD QUICK DESCRIPTION ABOUT THE PROJECT>

## Design principles

- Explicit typing everywhere: variables, function parameters, return values.
- Function names are verbs, variable names are nouns.
- Write understandable code, not clever code.
- Functions must be short (max 60 lines).
  <ADD OTHER DESIGN PRINCIPLES>

## Architecture

## Test-Driven Development

- All implementation must be testable and unit tests must exists and pass.

## Tasks & agents

This list of tasks can be found in `.claude/tasks/todo` and `.claude/tasks/done`. Done tasks provide history of my prompts. Todo tasks are the next envisonned steps.

**CRITITCAL** You can always look the vision ahead in written todo tasks, but we NEVER implement anything else that the very next step (first todo tasks, by alphabetic order). Other tasks are informative and may help making future-proof design decisions. If it leads to unecessary complexity, we just forget about them and act as if they were not written at all.

When a tasks involves enhancing the project (typically adding a new feature), a typical list of things to do is :

- Add the feature in the code.
- Add the relevant unit tests for the code.
- Run the unit tests to ensure that everything passes.
- Document in `README.md` for the humans.
- Potentially update the `CLAUDE.md` for yourself.
- Update the `CHANGELOG.md` with your changes and the task related to the change.
- Commit and mark the task done.

**IMPORTANT** If you block on something and are in autonomous mode, adapt the task with your analysis and questions, move it to `analyzed` and move to the next task.

**CRITICAL** Commit everytime you have something stable. You should end up having ONE commit per task. `Use commit --amend` if needed. NEVER have two different tasks commited together.
