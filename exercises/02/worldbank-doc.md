# World Bank Indicators API (문서 발췌, 실습용)

Base URL: `https://api.worldbank.org/v2/country/{country}/indicator/{indicator}`

- `country`: ISO 3166-1 alpha-3 code. Multiple countries can be joined with a semicolon. Use `all` for every country.
- `indicator`: World Bank indicator code, e.g. `SP.DYN.TFRT.IN`

Query parameters:

| name | description |
|---|---|
| `format` | `json` or `xml`. Default is xml. |
| `date` | Year or range, e.g. `2015` or `2015:2025` |
| `per_page` | Number of records per page. Default 50. |
| `page` | Page number, starting at 1. |

The JSON response is an array of two elements. The first element is an object with paging information: `page`, `pages`, `per_page`, `total`, `lastupdated`. The second element is an array of observation objects, each containing `indicator`, `country`, `countryiso3code`, `date`, `value`, `unit`, `obs_status` and `decimal`. A missing observation has `value` null.

No API key is required. Requests are not authenticated.
