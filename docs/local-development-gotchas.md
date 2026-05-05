# Local development gotchas

This page lists common local development issues and how do resolve them.

For broader local development guidance used across services, see the internal TNA Atlassian page below (requires TNA Atlassian access):
<https://national-archives.atlassian.net/wiki/spaces/TW/pages/775028742/Local+development>

## Catalogue Landing Page and Global Notifications

This app integrates with [ds-wagtail](https://github.com/nationalarchives/ds-wagtail) to display the catalogue landing page and global notifications across the application.

### API Endpoints Accessed

This app makes requests to the following Wagtail API endpoints:

- `GET /api/v2/globals/notifications/` - Fetches global alerts and mourning notices
- `GET /api/v2/catalogue/landing/` - Fetches landing page data including top pages and latest articles

These endpoints are accessed at the base URL configured via `WAGTAIL_API_URL`.

### Local Development Setup

To test the catalogue landing page and global notifications locally:

1. **Configure the Wagtail API URL:** Set `WAGTAIL_API_URL` to point to your local ds-wagtail instance:

   ```
   WAGTAIL_API_URL=http://host.docker.internal:8000/api/v2
   ```

   This is already configured in `docker-compose.yml` for local development.

2. **Set up ds-wagtail:** Follow the setup instructions in the [ds-wagtail repository](https://github.com/nationalarchives/ds-wagtail) to:
   - Install and run the ds-wagtail service
   - To run ds-wagtail using WSL2 (TODO: remove this step instruction until we have it documented approppriately elsewhere)

     ```
     $ docker compose up -d
     $ export AWS_PROFILE=[Your profile when you configure]
     $ aws sso login --profile=[Your profile when you configure]
     $ ./dev/pull
     ```

     The app will fetch development data from EC2 required to run ds-wagtail.

   - Create the required pages and global notifications through the Wagtail admin interface. See the ds-wagtail documentation for specific steps on creating:
     - A "Catalogue Landing" page (usually available on dev pull)
     - Global notification content (alerts, mourning notices)

### Clears Django cache on `ds-catalogue`

Clears all caches including Landing page, Global notifications caches

```
$ docker compose exec app poetry run python manage.py clearcache
```
