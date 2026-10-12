# Benchmarking

piri includes a reproducible benchmark framework.

## Basic benchmark

```bash
piri --benchmark DATASET
```

Measurements include:

- original size
- archive size
- compression ratio
- compression time
- extraction time
- throughput
- CPU time
- RSS telemetry where supported
- integrity result

## Reproducible corpus

Generate a deterministic corpus:

```bash
piri --make-benchmark-corpus ./corpus --benchmark-size-mb 1024
```

The corpus contains different data characteristics so a benchmark is not biased toward a single compression workload.

## Benchmark selection

```bash
piri --best smallest -i DATASET
piri --best fastest -i DATASET
piri --best extract-fast -i DATASET
piri --best balanced -i DATASET
```

Selection is dataset-dependent. There is no universally fastest or smallest archive format.

## Benchmark philosophy

Always record:

- hardware
- operating system
- native compressor versions
- processor count
- dataset checksum
- repetitions

Results from different systems should not be compared without considering these variables.
