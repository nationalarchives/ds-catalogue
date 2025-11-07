# TNA Python Django Search Application

## Setting up a local build

Local development is done in Docker.

### Before starting a build for the first time

```sh
cp .env.example .env
```

`.env` hold sensitive values. Please ask on the `ds-etna-dev` slack channel to get those values.

### Build and start the container

```sh
docker compose up -d
```

### Add the static assets

During the first time install, your `app/static/assets` directory will be empty.

As you mount the project directory to the `/app` volume, the static assets from TNA Frontend installed inside the container will be "overwritten" by your empty directory.

To add back in the static assets, run:

```sh
docker compose exec app cp -r /app/node_modules/@nationalarchives/frontend/nationalarchives/assets /app/app/static
```

### Preview application

<http://localhost:65533/>

### Preview docs

<http://localhost:65532/>

### Run tests

```sh
docker compose exec dev poetry run python manage.py test
```

### Format and lint code

```sh
docker compose exec dev format
```

## Environment variables

In addition to the [base Docker image variables](https://github.com/nationalarchives/docker/blob/main/docker/tna-python-django/README.md#environment-variables), this application has support for:

| Variable                          | Purpose                                               | Default                                                     |
| --------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------- |
| `DJANGO_SETTINGS_MODULE`          | The configuration to use                              | `config.settings.production`                                |
| `DEBUG`                           | If true, allow debugging                              | `False`                                                     |
| `COOKIE_DOMAIN`                   | The domain to save cookie preferences against         | _none_                                                      |
| `CSP_IMG_SRC`                     | A comma separated list of CSP rules for `img-src`     | `'self'`                                                    |
| `CSP_SCRIPT_SRC`                  | A comma separated list of CSP rules for `script-src`  | `'self'`                                                    |
| `CSP_STYLE_SRC`                   | A comma separated list of CSP rules for `style-src`   | `'self'`                                                    |
| `CSP_FONT_SRC`                    | A comma separated list of CSP rules for `font-src`    | `'self'`                                                    |
| `CSP_CONNECT_SRC`                 | A comma separated list of CSP rules for `connect-src` | `'self'`                                                    |
| `CSP_MEDIA_SRC`                   | A comma separated list of CSP rules for `media-src`   | `'self'`                                                    |
| `CSP_WORKER_SRC`                  | A comma separated list of CSP rules for `worker-src`  | `'self'`                                                    |
| `CSP_FRAME_SRC`                   | A comma separated list of CSP rules for `frame-src`   | `'self'`                                                    |
| `CSP_REPORT_URL`                  | The URL to report CSP violations to                   | `'self'`                                                    |
| `GA4_ID`                          | The Google Analytics 4 ID                             | _none_                                                      |
| `ROSETTA_API_VERIFY_CERTIFICATES` | Verify certificate for API                            | `True`                                                      |
| `ENVIRONMENT_NAME`                | The name of the environment (for reporting purposes)  | `production`                                                |
| `SENTRY_DSN`                      | The ID of the Sentry client project to catch issues   | _none_                                                      |
| `SENTRY_SAMPLE_RATE`              | How often to sample traces and profiles (0-1.0)       | production: `0.1`, staging: `0.25`, develop: `1`, test: `0` |

See [Sentry's official guide](https://docs.sentry.io/platforms/python/guides/django/) for further information on configuring Sentry for Django projects.

`.env` variables:

| Variable                   | Purpose                                                                    |
| -------------------------- | -------------------------------------------------------------------------- |
| `ROSETTA_API_URL`          | The base API URL for Rosetta, including the `/rosetta/data` path           |
| `WAGTAIL_API_URL`          | The base API URL for Wagtail                                               |
| `WAGTAIL_API_TIMEOUT`      | Maximum timeout of Wagtail api (seconds)                                   |
| `DELIVERY_OPTIONS_API_URL` | Api for Delivery options                                                   |
| `DCS_PREFIXES`             | Comma separated list of document prefixes for distressing content          |
| `STAFFIN_IP_ADDRESSES`     | Comma separated list of CIDR format IP addresses identifying staff access  |
| `ONSITE_IP_ADDRESSES`      | Comma separated list of CIDR format IP addresses identifying onsite access |
| `MAX_SUBJECTS_PER_RECORD`  | Maximum number of subjects displayed on details screen                     |

TODO: Find where the IP_ADDRESSES are documented and link to document here
