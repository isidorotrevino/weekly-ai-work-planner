#!/usr/bin/env python3
"""Review Git publication candidates without printing matching secret values.

Uses only the Python standard library. This is a narrow hygiene check, not a
replacement for maintained secret scanning, credential rotation, or diff review.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT_BYTES = 1_000_000
SECRET_PATTERNS = [
  ("private-key header", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----")),
  ("AWS access-key pattern", re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
  ("GitHub token pattern", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b")),
  ("API secret-key pattern", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}\b")),
  ("URL with embedded credentials", re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/:@]+:[^\s/@]{4,}@")),
  ("personal home-directory path", re.compile(r"/(?:home|Users)/[A-Za-z0-9_.-]+/")),
]
CREDENTIAL_ASSIGNMENT = re.compile(
  r'''(?im)\b(?:password|passwd|api[_-]?key|client[_-]?secret|access[_-]?token|auth[_-]?token)\b["']?\s*[:=]\s*["']([^"'\r\n]{12,})["']'''
)
PLACEHOLDERS = re.compile(r"(?i)(example|placeholder|dummy|synthetic|changeme|replace.?me|your[_-]|test[_-]|^\$\{|^<)")
PRIVATE_PARTS = {".aws", ".ssh", ".docker", ".terraform", ".azure", ".gcloud", ".kube", ".codex", ".agents", ".claude", "node_modules", "target", "build", "dist", "out", "coverage", "pgdata", "pg_data", "__pycache__", ".venv", ".m2", "secrets", "credentials"}
PRIVATE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".dump", ".backup", ".sqlite", ".sqlite3"}
PRIVATE_FILES = {".netrc", ".pgpass", ".npmrc", ".pypirc", ".git-credentials", "credentials.json", "id_rsa", "id_ed25519"}
LOCAL_PREFIXES = ("work/", "attachments/", "data/", "artifacts/", "exports/", "backups/", "tmp/", "temp/", "docs/internal/", "testing/D2/evidence/")


def publication_paths():
  result = subprocess.run(
    ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
    cwd=ROOT, check=True, capture_output=True,
  )
  return sorted(set(p.decode("utf-8", errors="surrogateescape") for p in result.stdout.split(b"\0") if p))


def check_path(name):
  path = Path(name)
  parts = set(path.parts)
  example = path.name.endswith(".example")
  if name.startswith(LOCAL_PREFIXES) or parts & PRIVATE_PARTS:
    return "private/generated directory is a publication candidate"
  if path.name in PRIVATE_FILES or path.suffix.lower() in PRIVATE_SUFFIXES:
    return "credential/database filename is a publication candidate"
  if path.name.startswith(".env") and not example:
    return "environment file is a publication candidate"
  if path.suffix in {".log", ".jar", ".class", ".zip"}:
    return "generated/archive artifact is a publication candidate"
  return None


def main():
  try:
    paths = publication_paths()
  except subprocess.CalledProcessError:
    print("Run this check inside the project Git checkout.", file=sys.stderr)
    return 2
  findings = []
  checked = 0
  for name in paths:
    path = ROOT / name
    reason = check_path(name)
    if reason:
      findings.append((name, None, reason))
      continue
    if path.is_symlink():
      findings.append((name, None, "review symlink before publication"))
      continue
    if not path.is_file():  # Tracked deletions are not publication content.
      continue
    if path.stat().st_size > MAX_TEXT_BYTES:
      findings.append((name, None, "large file needs explicit publication review"))
      continue
    data = path.read_bytes()
    if b"\0" in data:
      findings.append((name, None, "binary file needs explicit publication review"))
      continue
    content = data.decode("utf-8", errors="replace")
    checked += 1
    for label, pattern in SECRET_PATTERNS:
      for match in pattern.finditer(content):
        findings.append((name, content.count("\n", 0, match.start()) + 1, label))
    for match in CREDENTIAL_ASSIGNMENT.finditer(content):
      if not PLACEHOLDERS.search(match.group(1)):
        findings.append((name, content.count("\n", 0, match.start()) + 1, "possible embedded credential value"))
  if findings:
    print("Publication review required (matching values are not printed):")
    for name, line, reason in sorted(set(findings)):
      print(f"  {name}{':' + str(line) if line else ''}: {reason}")
    return 1
  print(f"Publication check passed: {checked} text files reviewed; no configured patterns found.")
  print("Review the staged diff before publishing; this check is not exhaustive.")
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
