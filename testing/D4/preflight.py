#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Read-only Docker/source preflight; never reports a functional lab PASS."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def query(args):
    try:
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                                timeout=15, check=False)
        # Do not copy daemon diagnostics, environment or local paths into reports.
        return {"ok": result.returncode == 0, "exit_code": result.returncode,
                "value": result.stdout.strip() if result.returncode == 0 else None}
    except FileNotFoundError:
        return {"ok": False, "error": "EXECUTABLE_UNAVAILABLE"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "QUERY_TIMEOUT"}


def main():
    os.umask(0o077)
    now = datetime.now(timezone.utc)
    run_id = "preflight-" + now.strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:8]
    destination = ROOT / "work" / "d4" / run_id
    destination.mkdir(parents=True, exist_ok=False)
    closure_path = ROOT / "docs/validation/D3-CLOSURE.json"
    closure = json.loads(closure_path.read_text())
    expected = dict(closure["verified_executable_input_sha256"])
    expected[closure["evidence"]["path"]] = closure["evidence"]["sha256"]
    mismatches = [name for name, digest in expected.items()
                  if not (ROOT / name).is_file() or sha(ROOT / name) != digest]
    patterns = ["migrations*/V*.sql", "scheduler-*/src/main/java/**/*.java",
                "testing/D4/**/*", "docs/design/D4-*.md", "worker-control-plane/src/**/*", "worker-runtime/src/**/*"]
    paths = {p for pattern in patterns for p in ROOT.glob(pattern)
             if p.is_file() and "__pycache__" not in p.parts}
    paths.update([ROOT / "pom.xml", ROOT / "scheduler-core/pom.xml",
                  ROOT / "scheduler-postgres/pom.xml", ROOT / "worker-control-plane/pom.xml", ROOT / "worker-runtime/pom.xml", closure_path])
    source_hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}
    docker = query(["docker", "version", "--format", "{{.Server.Version}}"])
    compose = query(["docker", "compose", "version", "--short"])
    images = {}
    for tag in ["postgres:16-bookworm", "maven:3.9-eclipse-temurin-21"]:
        observed = query(["docker", "image", "inspect", tag, "--format",
                          "{{json .Id}} {{json .RepoDigests}}"])
        images[tag] = observed
    infrastructure_ready = docker["ok"] and compose["ok"] and all(
        value["ok"] for value in images.values())
    ready = infrastructure_ready and not mismatches
    report = {
        "schema_version": "d4.preflight.v1", "recorded_at_utc": now.isoformat(),
        "run_id": run_id, "stage": "PREPARATION_ONLY",
        "result": "PREFLIGHT_READY" if ready else "PREFLIGHT_FAILED",
        "functional_scenarios_executed": 0, "D4_closed": False,
        "D3_closure_sha256": sha(closure_path), "D3_input_mismatches": mismatches,
        "source_sha256": source_hashes,
        "docker": docker, "compose": compose, "local_images": images,
        "limitations": ["This preflight executes no HTTPS/process/effect campaign or Compose",
                        "No Maven cache/build readiness claim",
                        "Historical hashes checked; historical tests not rerun",
                        "No exact reproduction claim from tags alone"]
    }
    output = destination / "preflight.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"result": report["result"], "report": output.relative_to(ROOT).as_posix(),
                      "functional_scenarios_executed": 0}, ensure_ascii=False))
    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
