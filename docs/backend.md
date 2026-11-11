# Backend development

## Template Variables

Template variables availale from the views are listed [here](backend/template_variables.md).

## Search

- [Pagination Limitations](backend/search-limitations.md) - Elasticsearch constraints and implementation details

## Markdown record details

Record details at `/catalogue/id/{id}/` support HTML and Markdown at the same URL. Request Markdown with the `Accept: text/markdown` header:

```sh
curl -H 'Accept: text/markdown' 'http://localhost:65533/catalogue/id/C123456/'
```

Negotiation uses Django's media-type parser, respecting quality values and specificity, with explicit `q=0` exclusions before wildcard matching. Missing or empty `Accept` headers default to HTML. When quality and specificity are equal, HTML wins regardless of header order.

If neither representation is acceptable, or a quality value is non-numeric or outside the range 0 to 1, the response is `406 Not Acceptable`.

Both representations, and 406 responses, include `Vary: Accept` so caches keep them separate.

Markdown uses `Content-Type: text/markdown; charset=utf-8` and is converted from the rendered main content, retaining the record's descriptions, links, access information and hierarchy without site headers, footers, hidden field descriptions or interactive controls.

Links are made absolute. Archive and creator details also support Markdown; related-record and help pages remain HTML-only.

## Backend resources

- [The National Archives base Docker images](https://github.com/nationalarchives/docker)
- [Digital Services Docker build actions](https://github.com/nationalarchives/ds-docker-actions)
