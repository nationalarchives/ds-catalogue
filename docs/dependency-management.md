# Dependency management

Using the app container should give you access to commands to update poetry which should update the `pyproject.toml` and/or `poetry.lock` files ready to commit to version control.

## Updating build numbers

e.g. `x.y.1` -> `x.y.2`

- Run `docker compose exec app poetry update` (Python)
  - alternatively, run `poetry update` on the docker host

## Major or minor numbers

e.g. `x.1.z` -> `x.2.z` or `1.y.z` -> `2.y.z`

- Update version numbers in `pyproject.toml` (Python)
- Run `docker compose exec app poetry update` (Python)
  - alternatively, run `poetry update` on the docker host

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

### Removing a dependency

```sh
docker compose exec app poetry remove DateTime
```
