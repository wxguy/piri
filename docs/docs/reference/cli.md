# Command Reference

## Core options

| Option | Description |
|---|---|
| `-i`, `--input` | Input directory or archive |
| `-o`, `--output` | Output archive or extraction directory |
| `-l`, `--list` | List archive contents |
| `-t`, `--test` | Test archive integrity without extracting |
| `-v`, `--verbose` | Verbose operation information |
| `-p`, `--processors` | Requested processor count |

## Safety and extraction

| Option | Description |
|---|---|
| `--overwrite` | `error`, `replace` or `skip` |
| `--atomic` | Stage extraction before committing destination |
| `--max-files` | Maximum extracted files |
| `--max-size-gb` | Maximum uncompressed data |
| `--max-path-length` | Maximum member path length |
| `--no-progress` | Disable progress reporting |

## Diagnostics

```bash
piri --version
piri --formats
piri --backends
piri --backends-json
piri --detect -i archive
piri --doctor
```

## Benchmarking

```bash
piri --benchmark DATASET
piri --benchmark-select -i DATASET
piri --best balanced -i DATASET
```

## Corpus generation

```bash
piri --make-benchmark-corpus ./corpus --benchmark-size-mb 1024
```

## Machine-readable output

```bash
piri --stats ...
```

JSON output is intended for automation and monitoring.
