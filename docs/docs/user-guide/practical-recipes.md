---
title: Practical recipes
description: Copy-ready piri examples for common daily, backup and automation tasks.
---

# Practical recipes

## Create a compressed backup

```bash
piri -i project -o project.tar.zst
```

## Extract to a new directory

```bash
piri -i project.tar.zst -o project-restored
```

## Inspect before extracting

```bash
piri -l -i project.tar.zst
piri -t -i project.tar.zst
```

## Refuse to overwrite anything

```bash
piri --overwrite error -i backup.tar.zst -o restored
```

## Replace existing files

```bash
piri --overwrite replace -i backup.tar.zst -o restored
```

## Skip existing files

```bash
piri --overwrite skip -i backup.tar.zst -o restored
```

## Use multiple processors

```bash
piri -p 8 -i data -o data.tar.zst
```

Parallelism is meaningful only when the selected backend supports it.

## Atomic extraction

```bash
piri --atomic -i backup.tar.zst -o restored
```

Atomic extraction stages the result and publishes the destination only after successful completion. The destination must not already exist.

## Produce machine-readable statistics

```bash
piri --stats -i data -o backup.tar.zst
```

Use JSON output where supported when integrating piri into automation.

## Detect an unknown file

```bash
piri --detect -i download.bin
```

## Ask piri what your machine supports

```bash
piri --doctor
piri --backends
piri --formats
```

## Benchmark your own dataset

```bash
piri --benchmark-select -i ./data
piri --best balanced -i ./data
```

Do not select a compression format solely because it is fast on someone else's benchmark. Dataset structure matters.
