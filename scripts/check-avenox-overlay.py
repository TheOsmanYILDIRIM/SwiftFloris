#!/usr/bin/env python3
"""Guard the SwiftFloris fork's thin Avenox overlay.

The fork is intentionally kept close to upstream. New fork-owned code belongs in
Avenox-owned paths. Any edit to an upstream-owned file must be explicitly listed
as an integration point and carry a stable AVENOX-HOOK marker.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".avenox" / "overlay.json"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def run_git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode != 0:
        fail(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def load_manifest() -> dict:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing manifest: {MANIFEST.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"invalid overlay manifest: {exc}")
    if data.get("schema") != 1:
        fail("unsupported .avenox/overlay.json schema")
    return data


def is_owned(path: str, manifest: dict) -> bool:
    if path in set(manifest.get("owned_files", [])):
        return True
    return any(path.startswith(prefix) for prefix in manifest.get("owned_prefixes", []))


def validate_integration_points(manifest: dict) -> set[str]:
    points = manifest.get("integration_points", [])
    if not isinstance(points, list):
        fail("integration_points must be a list")

    paths: set[str] = set()
    for index, point in enumerate(points):
        if not isinstance(point, dict):
            fail(f"integration_points[{index}] must be an object")
        path = point.get("path")
        marker = point.get("marker")
        if not path or not marker:
            fail(f"integration_points[{index}] requires path and marker")
        if not marker.startswith("AVENOX-HOOK:"):
            fail(f"integration marker must start with AVENOX-HOOK: ({path})")
        source = ROOT / path
        if not source.is_file():
            fail(f"integration point is missing: {path}")
        if marker not in source.read_text(encoding="utf-8"):
            fail(f"integration marker {marker!r} not found in {path}")
        paths.add(path)
    return paths


def validate_required_files(manifest: dict) -> None:
    for path in manifest.get("owned_files", []):
        if not (ROOT / path).is_file():
            fail(f"fork-owned required file is missing: {path}")


def validate_no_internet_permission() -> None:
    manifest = ROOT / "app" / "src" / "main" / "AndroidManifest.xml"
    if not manifest.is_file():
        fail("AndroidManifest.xml not found")
    text = manifest.read_text(encoding="utf-8")
    if 'android:name="android.permission.INTERNET"' in text:
        fail("Avenox overlay must not add android.permission.INTERNET")


def validate_diff(upstream_ref: str, manifest: dict, integration_paths: set[str]) -> None:
    changed = [
        line.strip()
        for line in run_git("diff", "--name-only", f"{upstream_ref}...HEAD").splitlines()
        if line.strip()
    ]
    unexpected = [
        path
        for path in changed
        if not is_owned(path, manifest) and path not in integration_paths
    ]
    if unexpected:
        print("Unexpected edits to upstream-owned files:", file=sys.stderr)
        for path in unexpected:
            print(f"  - {path}", file=sys.stderr)
        print(
            "Move fork-owned code under an Avenox-owned path or register the minimal "
            "upstream hook in .avenox/overlay.json with an AVENOX-HOOK marker.",
            file=sys.stderr,
        )
        raise SystemExit(1)
    print(f"Overlay diff guard: OK ({len(changed)} fork delta paths)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--upstream-ref",
        help="Git ref used to ensure all fork delta paths are owned or registered hooks",
    )
    args = parser.parse_args()

    manifest = load_manifest()
    validate_required_files(manifest)
    integration_paths = validate_integration_points(manifest)
    validate_no_internet_permission()
    if args.upstream_ref:
        validate_diff(args.upstream_ref, manifest, integration_paths)
    else:
        print("Overlay static guard: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
