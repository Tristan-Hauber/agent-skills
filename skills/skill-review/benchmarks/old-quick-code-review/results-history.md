# Historical skill-review benchmark results

Historical primary scores use QCR-1 through QCR-4. QCR-7 was discovered later and is not retroactively
included in those scores.

| Version | Primary | Secondary at the time | Notable calibration issues | Time | Effective message tokens |
|---|---:|---:|---|---:|---:|
| v3 | **4/4** | **2/2** | some overstatement/calibration issues | 5m20s | 47.2k main; worker cost unavailable |
| v4 | 3/4 | 1/2 | several overstatements/false-positive traps | 6m15s | ~189.9k |
| v5 | 1/4 | 1/2 | substantial recall regression | 7m55s | ~198.1k |
| v6 | 3/4 | 1/2 + QCR-7 newly discovered | still some behavioural overstatement | 5m40s | ~197.9k |

## Current canonical choice

The runtime core is based on **v3**, the observed local maximum on medium-effort primary recall.

Later infrastructure retained in the canonical package is documented in the top-level README.
