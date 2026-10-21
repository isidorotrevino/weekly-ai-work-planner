# Third-party notices

## D4 synthetic HTTPS adapter

`worker-control-plane/pom.xml` pins Spring Boot 4.1.1 and PostgreSQL JDBC 42.7.13.
The Bootstrap artifact contains Spring Framework 7.0.9, Tomcat 11.0.24 and Jackson
3.1.5 as managed dependencies. Their downloaded Maven metadata identifies Apache
License 2.0 for Spring/Boot, Tomcat and Jackson, and BSD-2-Clause for PostgreSQL JDBC.
Other managed runtime libraries retain their own licenses/notices in their nested
JARs. No upstream implementation was copied into repository source. Generated
artifacts and dependency caches stay in ignored `work/`; preserve their upstream
license/notice files if distributing a built application later. The D4 I2 evidence
records the observed packaged dependency names and hashes separately from tests.

The I4 synthetic lab also packages the already-pinned Flyway 13.10.3 core and
PostgreSQL module used by the validation harness. Preserve the license and notice
files embedded in those JARs; the laboratory image is a local validation artifact,
not a reviewed distribution. OpenSSL and Docker/Compose are host tooling.

## npm/node-semver 7.7.2

The proposed PostgreSQL SemVer range expansion in V11 follows the algorithm in
[npm/node-semver 7.7.2](https://github.com/npm/node-semver/tree/v7.7.2),
commit `281055e7716ef0415a8826972471331989ede58c`. The reference used for differential
tests is downloaded to ignored `work/`; it is not a production dependency.
The generated conformance fixture includes cases from its upstream test fixtures.

ISC License

Copyright (c) Isaac Z. Schlueter and Contributors

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

## Git in the D4 I12 laboratory

The Java fixture verifier invokes the native Git executable already present in
the pinned Maven/Temurin laboratory image as a separate process. No Git source
implementation is copied into this repository. Its observed version is recorded
with the I12 evidence. Preserve the image/package's upstream copyright, license
and notice files if distributing a laboratory image; the current image remains
a local synthetic validation artifact, not a reviewed distribution.

## Local development diagnostic relay

The development Compose entry point additionally uses the digest-pinned official
Python 3.12 slim image for a repository-owned TCP relay built with Python's standard
library. It terminates no TLS and includes no third-party Python packages. Preserve
the runtime image's Python and operating-system license/notice files if distributing
an image later; this environment is currently a local development artifact.
