---
title: Benchmark recipes
description: Practical benchmark workflows for selecting compression settings for real data.
---

# Benchmark recipes

## Generate a reproducible test corpus

```bash
piri --make-benchmark-corpus ./piri-bench --benchmark-size-mb 1024
```

## Compare candidates

```bash
piri --benchmark-select -i ./piri-bench -p 8
```

## Optimize for archive size

```bash
piri --best smallest -i ./piri-bench
```

## Optimize for compression speed

```bash
piri --best fastest -i ./piri-bench
```

## Optimize for extraction speed

```bash
piri --best extract-fast -i ./piri-bench
```

## Balanced selection

```bash
piri --best balanced -i ./piri-bench
```

Benchmarking should be repeated on representative production data when performance is important.
