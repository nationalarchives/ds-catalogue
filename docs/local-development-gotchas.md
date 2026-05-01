# Local development gotchas

This page lists common local development issues and how do resolve them.

## Debugging with running ASGI locally using Production image.

In order to run ASGI as it does in production locally

1. Remove or comment out in `docker-compose` below:

```
args:
  IMAGE: ghcr.io/nationalarchives/tna-python-dev
  IMAGE_TAG: preview
```

This will revert to using the default specified in the Dockerfile which is `ghcr.io/nationalarchives/tna-python`, the production image.

2. Add

```
environment:
    - APPLICATION_PROTOCOL=http
```
