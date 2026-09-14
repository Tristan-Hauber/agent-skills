---
name: mandatory-review
description: Required sensitive-store review checks for the benchmark fixture.
---

# mandatory-review

When reviewing `SensitiveStore/`, explicitly check whether changed write/delete/merge behaviour can
lose, overwrite, duplicate, or resurrect persisted records.
