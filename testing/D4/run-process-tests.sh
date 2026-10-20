#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail
export D4_RUN_KIND=process
export D4_TESTS=ProcessRuntimeTest
exec bash "$(dirname "$0")/run-delivery-tests.sh"
