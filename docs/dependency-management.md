# Dependency management

Using the app container should give you access to commands to update poetry which should update the `pyproject.toml` and/or `poetry.lock` files ready to commit to version control.

**Note**

To provide a cooling-off period for newly published dependencies, Poetry is configured with `POETRY_SOLVER_MIN_RELEASE_AGE`, which is set through an image environment variable derived from `COOLDOWN_PERIOD`.

The default value is the recommended setting and should only be changed following discussion and approval. Reducing this value increases the likelihood of consuming very recent package releases.

## Updating build numbers

e.g. `x.y.1` -> `x.y.2`

- If the app container is already running
  - Run `docker compose exec app poetry update` (Python)
- Alternatively, run `poetry update` on the docker host
- Alternatively, start a temporary app container to run the update:
  - Run `docker compose run --rm app poetry update`
  - Run `docker compose up -d --build app`

## Major or minor numbers

e.g. `x.1.z` -> `x.2.z` or `1.y.z` -> `2.y.z`

- Update version numbers in `pyproject.toml` (Python)
- If the app container is already running
  - Run `docker compose exec app poetry update` (Python)
- Alternatively, run `poetry update` on the docker host
- Alternatively, start a temporary app container to run the update:
  - Run `docker compose run --rm app poetry update`
  - Run `docker compose up -d --build app`

## Adding a dependency

Use the following to automatically use the latest version (e.g. [pendulum](https://pypi.org/project/pendulum/)):

```sh
docker compose exec app poetry add DateTime
```

Or, specify a version:

```sh
docker compose exec app poetry add DateTime@4.1.1
docker compose exec app poetry add "DateTime@>=4.0"
```

Or, to a group

```sh
docker compose exec dev poetry add --group <group-name> <package-name>
```

See the [Poetry docs](https://python-poetry.org/docs/cli/#add) for more options.

## Removing a dependency

```sh
docker compose exec app poetry remove DateTime
```
