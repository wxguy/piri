from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import sys
import time
from pathlib import Path

from . import __version__
from .backends import backend_info
from .detect import detect_format
from .formats import all_formats, from_extension, get_format
from .engine import ArchiveEngine
from .policy import ExtractionPolicy
from .metadata import MetadataPolicy
from .progress import Progress


class _PiriArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        if message.startswith("unrecognized arguments:"):
            message += "; provide input paths with -i PATH or --input PATH"
        super().error(message)


def parser():
    p = _PiriArgumentParser(prog="piri", description="Practical, secure archive compression and extraction")
    p.add_argument("-i", "--input", help="input directory or archive")
    p.add_argument("-o", "--output", help="output archive or extraction directory")
    p.add_argument("-l", "--list", action="store_true", help="list archive contents")
    p.add_argument("-t", "--test", action="store_true", help="test archive integrity without extracting")
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("-p", "--processors", type=int, default=1)
    p.add_argument("--overwrite", choices=["error", "replace", "skip"], default="error")
    p.add_argument("--max-files", type=int, default=1_000_000)
    p.add_argument("--max-size-gb", type=float, default=100.0)
    p.add_argument("--max-path-length", type=int, default=4096)
    p.add_argument("--max-members", type=int, default=1_000_000)
    p.add_argument("--no-progress", action="store_true", help="disable progress output")
    p.add_argument("--stats", action="store_true", help="print operation statistics as JSON")
    p.add_argument("--atomic", action="store_true", help="extract into a staging directory and atomically create a new destination")
    p.add_argument("--preserve-mode", action="store_true")
    p.add_argument("--preserve-mtime", action="store_true")
    p.add_argument("--preserve-owner", action="store_true")
    p.add_argument("--preserve-xattrs", action="store_true")
    p.add_argument("--formats", action="store_true")
    p.add_argument("--backends", action="store_true")
    p.add_argument("--backends-json", action="store_true", help="print backend capabilities as JSON")
    p.add_argument("--detect", action="store_true")
    p.add_argument("--doctor", action="store_true")
    p.add_argument("--best", choices=["smallest", "fastest", "extract-fast", "balanced"])
    p.add_argument("--benchmark-select", action="store_true")
    p.add_argument("--benchmark-repeats", type=int, default=3)
    p.add_argument("--benchmark-json", action="store_true")
    p.add_argument("--make-benchmark-corpus", metavar="DIR", help="create a deterministic benchmark corpus")
    p.add_argument("--benchmark-size-mb", type=int, default=64, help="size of generated benchmark corpus (MiB)")
    p.add_argument("--benchmark-seed", type=int, default=12345, help="seed for generated benchmark corpus")
    p.add_argument("--version", action="version", version=__version__)
    return p


def show_formats():
    print(f"{'Format':<12} {'Read':<5} {'Write':<6} {'Avail':<6} {'C-Par':<6} {'E-Par':<6} Backend")
    print("-" * 88)
    for f in all_formats():
        print(f"{f.name:<12} {str(f.read):<5} {str(f.write):<6} {str(f.available()):<6} "
              f"{str(f.parallel_compression):<6} {str(f.parallel_extraction):<6} {f.backend}")


def show_backends():
    engine = ArchiveEngine()
    print(f"{'Backend':<12} {'Format':<12} {'Avail':<6} {'Read':<5} {'Write':<6} {'Test':<5} {'C-Par':<6} {'E-Par':<6} {'Stream':<7} Executable")
    print("-" * 112)
    for row in engine.backend_capabilities():
        print(f"{row['backend']:<12} {row['format']:<12} {str(row['available']):<6} {str(row['read']):<5} "
              f"{str(row['write']):<6} {str(row['test']):<5} {str(row['parallel_compression']):<6} "
              f"{str(row['parallel_extraction']):<6} {str(row['streaming']):<7} {row['executable'] or '-'}")

def show_backends_json():
    engine = ArchiveEngine()
    print(json.dumps({"backends": engine.backend_capabilities(),
                      "plugin_load_errors": engine.registry.load_errors}, indent=2))


def doctor():
    print(f"piri {__version__}")
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print(f"CPU count: {os.cpu_count()}")
    for cmd in ("tar", "pigz", "gzip", "zstd", "xz", "bzip2", "pbzip2", "lz4", "zip", "7z", "7zz", "cpio", "ar", "bsdtar", "unrar", "lha", "uncompress"):
        print(f"{cmd:<12} {shutil.which(cmd) or '-'}")


def _policy(args) -> ExtractionPolicy:
    if args.processors < 1:
        raise SystemExit("-p/--processors must be >= 1")
    if args.max_files < 1 or args.max_members < 1 or args.max_path_length < 1 or args.max_size_gb <= 0:
        raise SystemExit("resource limits must be positive")
    return ExtractionPolicy(
        overwrite=args.overwrite,
        max_files=args.max_files,
        max_total_bytes=int(args.max_size_gb * 1024**3),
        max_path_length=args.max_path_length,
        max_members=args.max_members,
    )


def main(argv=None):
    p = parser()
    args = p.parse_args(argv)
    if args.formats:
        show_formats(); return 0
    if args.make_benchmark_corpus:
        if args.benchmark_size_mb < 1:
            raise SystemExit("--benchmark-size-mb must be >= 1")
        from .corpus import create_benchmark_corpus
        print(json.dumps(create_benchmark_corpus(args.make_benchmark_corpus, size_mb=args.benchmark_size_mb, seed=args.benchmark_seed), indent=2))
        return 0
    if args.backends_json:
        show_backends_json(); return 0
    if args.backends:
        show_backends(); return 0
    if args.doctor:
        doctor(); return 0
    if args.detect:
        if not args.input:
            raise SystemExit("--detect requires -i/--input")
        d = detect_format(args.input)
        print(json.dumps({"format": d.name, "confidence": d.confidence, "reason": d.reason}, indent=2))
        return 0

    if args.best or args.benchmark_select or args.benchmark_json:
        if not args.input:
            raise SystemExit("--best/--benchmark-select requires -i/--input")
        inp = Path(args.input)
        if not inp.is_dir():
            raise SystemExit("--best/--benchmark-select requires a directory input")
        from .selection import benchmark_candidates, rank_results, result_dicts
        results = benchmark_candidates(inp, jobs=max(1, args.processors), repeats=max(1, args.benchmark_repeats))
        mode = args.best or "balanced"
        ranked = rank_results(results, mode)
        if args.benchmark_json:
            print(json.dumps({"mode": mode, "dataset": str(inp), "repeats": max(1, args.benchmark_repeats),
                              "results": result_dicts(ranked)}, indent=2))
            return 0
        if args.benchmark_select:
            print(f"{'Rank':<5} {'Format':<12} {'Status':<7} {'Size(MiB)':>11} {'Ratio':>8} {'Comp(s)':>9} {'Ext(s)':>9} {'Score':>8}")
            print("-" * 88)
            for r in ranked:
                score = f"{r.score:.3f}" if r.score is not None else "-"
                print(f"{r.rank or '-':<5} {r.format:<12} {r.status:<7} {r.archive_bytes/1048576:>11.2f} "
                      f"{r.ratio:>8.2f} {r.compression_seconds:>9.3f} {r.extraction_seconds:>9.3f} {score:>8}")
        if args.best:
            chosen = ranked[0]
            print(json.dumps({"mode": args.best, "format": chosen.format, "archive_bytes": chosen.archive_bytes,
                              "ratio": round(chosen.ratio, 3), "compression_seconds": round(chosen.compression_seconds, 4),
                              "extraction_seconds": round(chosen.extraction_seconds, 4),
                              "score": round(chosen.score, 4) if chosen.score is not None else None,
                              "integrity": chosen.integrity}, indent=2))
        return 0

    if args.test:
        if not args.input:
            raise SystemExit("--test requires -i/--input")
        inp = Path(args.input)
        if not inp.is_file():
            raise SystemExit("--test requires an archive file as input")
        try:
            result = ArchiveEngine().test(inp)
        except Exception as exc:
            if args.verbose:
                print(f"integrity test FAILED: {exc}")
            else:
                print(f"piri: integrity test failed: {exc}", file=sys.stderr)
            return 1
        if args.stats:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(f"OK: {inp} ({result.format}, {result.members_processed} members)")
            if args.verbose:
                print(f"tested {inp} in {result.elapsed_seconds:.3f}s")
        return 0

    if not args.input:
        p.error("no input provided; use -i PATH or --input PATH")
    inp = Path(args.input)
    engine = ArchiveEngine()

    if args.list:
        for name in engine.list(inp):
            print(name)
        return 0

    if inp.is_dir():
        if not args.output:
            raise SystemExit("compression requires -o/--output")
        out = Path(args.output)
        spec = from_extension(str(out))
        if not spec or not spec.write:
            raise SystemExit(f"cannot determine a writable archive format from: {out}")
        if not spec.available():
            raise SystemExit(f"format backend is unavailable: {spec.name}")
        if args.processors < 1:
            raise SystemExit("-p/--processors must be >= 1")
        progress = Progress(enabled=not args.no_progress, label="compress")
        t0 = time.monotonic()
        fmt = engine.create(inp, out, jobs=args.processors, metadata=MetadataPolicy(
            args.preserve_mode, args.preserve_mtime, args.preserve_owner, args.preserve_xattrs), progress=progress)
        if args.stats:
            print(json.dumps(fmt.to_dict() if hasattr(fmt, "to_dict") else {"format": str(fmt)}, indent=2))
        elif args.verbose:
            print(f"created {out} ({fmt}) in {time.monotonic()-t0:.3f}s")
        return 0

    if inp.is_file():
        out = Path(args.output) if args.output else inp.with_suffix("")
        progress = Progress(enabled=not args.no_progress, label="extract")
        t0 = time.monotonic()
        fmt = engine.extract(inp, out, policy=_policy(args), jobs=args.processors, atomic=args.atomic, metadata=MetadataPolicy(
            args.preserve_mode, args.preserve_mtime, args.preserve_owner, args.preserve_xattrs), progress=progress)
        if args.stats:
            print(json.dumps(fmt.to_dict() if hasattr(fmt, "to_dict") else {"format": str(fmt)}, indent=2))
        elif args.verbose:
            print(f"extracted {inp} -> {out} ({fmt}) in {time.monotonic()-t0:.3f}s")
        return 0

    raise SystemExit(f"input does not exist: {inp}")


if __name__ == "__main__":
    raise SystemExit(main())
