# Claude Development Guide for marne-battle-web

This document providers instructions for AI assistants (like Claude) working on marne-battle-web.

## Project Overview

This is a migration project of the website https://www.sambre-marne-yser.be/ from Spip to Jekyll static website. The Spip environment is not available and broken on some part. The only way to get the content is by using the Internet Archive (https://archive.org). The goal is to assemble the original content from the Internet Archive, convert these into a Markdown static content and then use Jekyll to build a static website that will last forever.

## Design principles

- Explicit typing everywhere: variables, function parameters, return values.
- Function names are verbs, variable names are nouns.
- Write understandable code, not clever code.
- Functions must be short (max 60 lines).

## Website structure on Spip

The website https://www.sambre-marne-yser.be/ is hosted on Spip.

It is composed by the "homepage" on the URL https://www.sambre-marne-yser.be/ or https://www.sambre-marne-yser.be/sommaire.php3. The "homepage" is composed by the content (text and pictures) and the links to the "pages".

The "pages" are accessible from the "homepage". The URLs are under the form https://www.sambre-marne-yser.be/page_XX.php3 (XX is a 2-digit number 01, 02, etc). A "page" is composed by links to "articles". Each "article" is composed by a title, a summary and a link to read more ("Lire la suite"). The link "Lire la suite" is a link to the "article".

The "articles" are accessible from the "pages". The URLs are under the form https://www.sambre-marne-yser.be/article=XX.php3?id_article=YY where XX is a number of the "page" (1, 2, etc) and YY is the number of the "article". An "article" is composed by the content (text and pictures).

The structure of the Spip website is composed by: 1 homepage -> X pages -> Y articles.

The problem with the official URL is a broken MySQL instance; so, there are pages and articles unavailable. This is why we must download the content from https://archive.org. The website didn't evolve since the death of the creator in 2009. Therefore, all downloads from https://archive.org must be performed after 2010 and before 2015.

## Architecture

### Language and environment

- Programs are written in Python
- The virtual environment is defined in `venv`.
- The required libraries are defined in `requirements.txt` and installed automatically in the virtual environment with the `./scripts/venv.sh` script.
- To create or recreate the Virtual Environment, use `./scripts/venv.sh` script.
- To run the linter, use `./scripts/lint.sh`
- To run the test, use `./scripts/test.sh`

## Test-Driven Development

- All implementation must be testable and unit tests must exists and pass.

## Tasks & agents

This list of tasks can be found in `.claude/tasks/todo` and `.claude/tasks/done`. Done tasks provide history of my prompts. Todo tasks are the next envisonned steps.

**CRITITCAL** You can always look the vision ahead in written todo tasks, but we NEVER implement anything else that the very next step (first todo tasks, by alphabetic order). Other tasks are informative and may help making future-proof design decisions. If it leads to unecessary complexity, we just forget about them and act as if they were not written at all.

When a tasks involves enhancing the project (typically adding a new feature), a typical list of things to do is :

- Add the feature in the code.
- Add the relevant unit tests for the code.
- Run the linter and ensure that everything passes.
- Run the unit tests and ensure that everything passes.
- Document in `README.md` for the humans.
- Potentially update the `CLAUDE.md` for yourself.
- Update the `CHANGELOG.md` with your changes and the task related to the change.
- Commit and mark the task done.

**IMPORTANT** If you block on something and are in autonomous mode, adapt the task with your analysis and questions, move it to `analyzed` and move to the next task.

**CRITICAL** Commit everytime you have something stable. You should end up having ONE commit per task. `Use commit --amend` if needed. NEVER have two different tasks commited together.
