from __future__ import annotations

import argparse
from pathlib import Path

from .io import load_manifest, repository_root
from .validate import validate_repository


def _validate(_: argparse.Namespace) -> int:
    errors = validate_repository()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"validation failed: {len(errors)} error(s)")
        return 1
    print("validation passed")
    return 0


def _describe(path: Path, document: Path | None = None) -> int:
    manifest = load_manifest(path)
    print(f"{manifest['id']}: {path}")
    if document is not None:
        print(document)
    return 0


def _report(args: argparse.Namespace) -> int:
    root = repository_root()
    run = (root / args.run).resolve()
    manifest_path = run / "run.yaml"
    manifest = load_manifest(manifest_path)
    declared = manifest.get("review", {}).get("report")
    if declared:
        report = (run / declared).resolve()
    elif (run / "REPORT.md").is_file():
        report = run / "REPORT.md"
    else:
        report = run / "README.md"
    return _describe(manifest_path, report)


def _compare(args: argparse.Namespace) -> int:
    spec = Path(args.spec).resolve()
    manifest = load_manifest(spec)
    return _describe(spec, (spec.parent / manifest["report"]).resolve())


def _collect(args: argparse.Namespace) -> int:
    root = repository_root()
    run = (root / args.run).resolve()
    results = Path(args.results).resolve()
    if not (run / "run.yaml").is_file():
        raise SystemExit(f"run manifest does not exist: {run / 'run.yaml'}")
    if not results.is_file():
        raise SystemExit(f"results file does not exist: {results}")
    destination = run / "raw" / "results" / results.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(results.read_bytes())
    print(destination)
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="python -m drawing_eval")
    commands = result.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="validate all cases, runs, comparisons, hashes, and links")
    validate.add_argument("--all", action="store_true", help="validate the whole repository")
    validate.set_defaults(func=_validate)
    report = commands.add_parser("report", help="locate a run manifest and its report")
    report.add_argument("--run", required=True)
    report.set_defaults(func=_report)
    compare = commands.add_parser("compare", help="locate a comparison specification and report")
    compare.add_argument("--spec", required=True)
    compare.set_defaults(func=_compare)
    collect = commands.add_parser("collect", help="import a raw harness result into an existing run")
    collect.add_argument("--run", required=True)
    collect.add_argument("--results", required=True)
    collect.set_defaults(func=_collect)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    return args.func(args)
