#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "$0")/../.." && pwd)"
maven_image="${D3_MAVEN_IMAGE:-maven:3.9-eclipse-temurin-21}"
cache_dir="${D3_MAVEN_CACHE:-$project_root/work/d3-core/m2}"
mkdir -p "$cache_dir"
cache_dir="$(cd "$cache_dir" && pwd)"
args=(run --rm --user "$(id -u):$(id -g)" -e MAVEN_CONFIG=/tmp/maven -e HOME=/tmp
      -e MAVEN_BIN=mvn -e D3_MAVEN_CACHE=/maven-cache -e "D3_OFFLINE=${D3_OFFLINE:-0}"
      --mount "type=bind,src=$project_root,dst=/project"
      --mount "type=bind,src=$cache_dir,dst=/maven-cache" --workdir /project)
if [[ "${D3_OFFLINE:-0}" == 1 ]]; then args+=(--network none --pull never); fi
docker "${args[@]}" "$maven_image" bash testing/D3/run-core-tests.sh
