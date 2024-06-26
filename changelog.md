<!--
SPDX-FileCopyrightText: 2024 Charles Crighton <code@crighton.net.nz>

SPDX-License-Identifier: MIT
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [x.y.z] - yyyy-mm-dd
### Added
### Changed
### Removed
### Fixed
-->

## [Unreleased]

## [0.0.5] - 2023-06-26

### Added
- Support for TLS
  - Added example [ssl](/example/ssl)
- Session based authentication support using cookies
  - Added @login_required decorator
  - Added example [auth](/examples/auth)


## [0.0.4] - 2023-10-04

### Added
- Refactored Phew as a class to support multiple apps with asyncio

### Changed
- Document approach to processing list in templates
- Additional common mime types mapped to extensions

### Fixed
- Ensure that all form data is read to content-length

<!-- Links -->
[Unreleased]: https://github.com/ccrighton/phew/compare/v0.0.5...HEAD

[0.0.5]: https://github.com/ccrighton/phew/releases/tag/v0.0.5
[0.0.4]: https://github.com/ccrighton/phew/releases/tag/v0.0.4
