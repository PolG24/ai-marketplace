"""Run with python3 -m manifest_validator path/to/manifest.json."""

import argparse
import sys
from pathlib import Path

from .validator import InputError, Issue, parse_manifest, validate_manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate an AI marketplace manifest against the static pilot policy.")
    parser.add_argument("manifest", type=Path, help="local JSON manifest file")
    args = parser.parse_args(argv)
    try:
        manifest = parse_manifest(args.manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        issues = [Issue("$", "input_error", "Cannot read the manifest as a UTF-8 file")]
        status = 2
    except InputError as exc:
        issues = [exc.issue]
        status = 2
    else:
        issues = validate_manifest(manifest)
        status = 1 if issues else 0

    if issues:
        print("REJECTED", file=sys.stderr)
        for issue in issues:
            print(f"{issue.path} [{issue.code}]: {issue.message}", file=sys.stderr)
    else:
        print("PASS: static pilot validation only; production approval is still required.")
    return status


if __name__ == "__main__":
    sys.exit(main())
