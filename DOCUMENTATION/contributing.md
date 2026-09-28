[← Project Guide](README.md)

# Contributing

How we work in this repository: git, writing, and where information goes.

## Git

- Commit straight to `main`. We use no feature branches or pull requests, so the history is one straight line of commits.
- Several people push to this repository and to the site repository. If a push is refused because someone else pushed first, pull and push again.
- Never force-push. It can erase someone else's commits.
- Explain why a change was made in its commit message, not in the docs or comments.

## Writing docs and comments

- Write plain English. Use short sentences, one idea each.
- Say what the problem is before saying what the code does about it.
- Avoid slang and clever phrasing, such as "baked in" or "the catch is". Say what happens.
- Leave internal names, such as LaTeX macros, out of how-to text unless the reader has to type them.
- Describe what is true now. Leave out history, such as "used to" or "after the split". That belongs in the commit message.
- Leave measurements that apply to one book out of shared files. They go out of date when the book changes.

## Where information goes

Each fact has one home. If something is already written down, link to it instead of repeating it.

- `DOCUMENTATION/README.md` is the map, with one line per page.
- [`customizations.md`](customizations.md) lists what this repository changes in PreTeXt.
- Comments in the code explain how that code works.
- [`reference/`](reference/) explains why a decision was made, with measurements and rejected alternatives.

Project notes, such as how an image license was checked, go in `DOCUMENTATION/`, for example next to the related task in [`pending-tasks.md`](pending-tasks.md). Don't put them in comments in `.ptx` files, where nobody looks for them.

`DOCUMENTATION/` is the guide for everyone, people and AI tools alike. Don't add files meant for one tool, such as `CLAUDE.md`. Put the guidance here.
