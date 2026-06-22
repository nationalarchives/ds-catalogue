# Project conventions

At TNA we follow a set of conventions for our projects to ensure consistency and quality across our codebases. These can be found in our [Engineering handbook](https://nationalarchives.github.io/engineering-handbook/) and should be followed when contributing to the project, as well as the guidance below.

## Python

### Formatting/Linting

This project uses a few tools to improve the consistency and quality of Python code:

- [`Ruff`](https://docs.astral.sh/ruff/): An extremely fast Python linter and code formatter, written in Rust.

```console
docker compose exec app format
```

This will be checked by CI on every commit, so it's a good idea to run this locally before pushing your changes.

Useful links

- <https://github.com/nationalarchives/docker/tree/main/docker/tna-python-dev#ruff>
- <https://nationalarchives.github.io/engineering-handbook/technology/backend/python/>

Configuration

- The project uses the department-wide Ruff configuration as a base. No additional installation is needed for development. It is included in the dev docker image.
- Project-level configuration may extend this base where necessary.
- Configuration is defined in ruff.toml that extends the base configuration.

Guidelines

- Always run formatting locally before pushing changes.
- CI will enforce formatting and linting on every commit

Important Notes:

- Do not use inline overrides such as # fmt: off/on or # noqa unless explicitly agreed by the team. Consistency is prioritised over individual formatting preferences.
- If a rule significantly impacts readability or developer experience, raise it for team discussion rather than bypassing it locally.
- Existing rule ignores (if any) are considered temporary and should be reduced over time.

## Git/Github conventions

### Signed Commits

    Ensure commits are signed before pushing to GitHub
    See 4. Security <https://nationalarchives.github.io/engineering-handbook/third-party/github/>

### Branching

- Changes are developed in feature branches and submitted as pull requests via Github
- Feature branches should always be based on: `main`
- Create a new branch if the branch for that ticket has been merged.

### Naming branches

- Use only alphanumeric characters and hyphens where possible and avoid special characters.
- Branch names for ticketed new features should follow: `feature/JIRA-TICKET-NUMBER-with-short-description`
- Branch names for ticketed bug fixes should follow: `fix/JIRA-TICKET-NUMBER-with-short-description`
- Branch names for housekeeping tasks or other unticketed work should follow: `chore/short-description`

For example:

- `feature/UN-123-extra-squiggles`
- `fix/DF-999-image-view-error`
- `chore/update-documentation`

### Naming pull requests

- Pull requests for features and bug fixes should be titled: `JIRA-TICKET-NUMBER: short-description`
- Pull requests for housekeeping tasks or other unticketed work should be titled: `CHORE: short-description`

For example:

- `UN-123: Add extra squiggles`
- `DF-999: Fix image view error`
- `CHORE: Update documentation`

### Merging branches

**NOTE:** Where possible, a feature branch should be kept up-to-date with `main` by regularly merging `main` into the feature branch. This will help to prevent conflicts when merging the feature branch back into `main`, and ensure there are no inconsistencies.

- When merging a feature branch into `main`, use the `Squash and merge` option to keep the commit history clean
