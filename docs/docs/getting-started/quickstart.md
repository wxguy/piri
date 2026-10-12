# Quick Start

## Create an archive

```bash
piri -i project/ -o project.tar.zst
```

## Extract an archive

```bash
piri -i project.tar.zst -o restored/
```

## List contents

```bash
piri -l -i project.tar.zst
```

## Test integrity

```bash
piri -t -i project.tar.zst
```

A successful test exits with status `0`. A failed integrity test exits non-zero.

## Verbose operation

```bash
piri -v -i project/ -o project.tar.zst
```

## Select processor count

```bash
piri -p 8 -i project/ -o project.tar.zst
```

The processor setting is passed only to backends that genuinely support parallel operation.

## Atomic extraction

```bash
piri --atomic -i project.tar.zst -o restored/
```

The destination is staged first and committed only after successful extraction.

## Statistics

```bash
piri --stats -i project/ -o project.tar.zst
```

This produces structured JSON suitable for scripts and monitoring.
