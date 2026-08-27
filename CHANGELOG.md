# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries for 0.0.1 to 0.0.3 are derived from the GitHub release notes.

## [Unreleased]

### Added

- `get_ip_address()` for the current STA address
- `server.stop()` and `server.close()`
- `package.json` so phew can be installed with `mip`
- ruff and codespell linting, and a test suite, in CI

### Changed

- Canonical `asyncio` and `socket` module names; MicroPython v1.29.0 dropped the
  `u`-prefixed aliases, so `usocket` no longer imports
- `logging` no longer enables `LOG_DEBUG` by default
- Packaging moved to `pyproject.toml` with hatchling, a git-derived version, and
  PyPI trusted publishing. The package is minified on the way into the sdist and
  wheel, roughly halving what lands on the device

### Removed

- `phew.ntp`; the Pico MicroPython build provides `ntptime`

### Fixed

- Responses no longer share a single headers dict. Every `Response` and
  `FileResponse` defaulted `headers` to `{}`, so `add_header` mutated the one
  default instance and headers leaked between responses - a streamed body, which
  sets no `Content-Length` of its own, inherited whatever the previous response
  set and clients truncated or hung
- `FileResponse` no longer returns from `__init__`, which MicroPython rejects
  with `TypeError: __init__() should return None` when `os.stat` raises
- A request that matched no route with no catchall registered, or a handler that
  returned nothing, left `response` as `None` and raised `AttributeError` before
  reaching `writer.close()`, leaking the socket. Now 404 and 500 respectively,
  and the connection always closes
- All form data is read up to `content-length`
- `_parse_query_string` splits only on the first `=`

## [0.0.3] - 2022-09-02

### Added

- `ntp.fetch(synch_with_rtc=True, timeout=10)` for NTP time synchronisation
- `set_truncate_thresholds(truncate_at, truncate_to)` for log truncation
- `access_point(ssid, password=None)` to put the Pico W into access point mode

### Changed

- Log files truncate automatically, at 11kB down to 8kB
- Template variables avoid `eval()` when present in the parameters dictionary
- Template expressions have leading and trailing whitespace stripped
- Log entries include free memory by default

## [0.0.2] - 2022-08-18

### Added

- Packaging for PyPI

## [0.0.1] - 2022-08-18

### Fixed

- `_parse_query_string` splits only on the first `=`

[Unreleased]: https://github.com/pimoroni/phew/compare/v0.0.3...HEAD
[0.0.3]: https://github.com/pimoroni/phew/releases/tag/v0.0.3
[0.0.2]: https://github.com/pimoroni/phew/releases/tag/v0.0.2
[0.0.1]: https://github.com/pimoroni/phew/releases/tag/v0.0.1
