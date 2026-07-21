# Caching

# Overview

| Key                | Description                      |
| ------------------ | -------------------------------- |
| SUBJECTS_CACHE_KEY | Cached data for grouped subjects |

# Cache invalidation

- Expires automatically after TTL
- Can be manually cleared using:
  - Django shell - `docker compose exec app poetry run python manage.py shell`

## Debugging

### Verify a cache exists

```
from django.core.cache import cache

cache.get("<KEY>")
```

### Clear cache

```
from django.core.cache import cache

cache.delete("<KEY>")
```

### Clear all caches

```
from django.core.cache import cache

cache.clear()
```
