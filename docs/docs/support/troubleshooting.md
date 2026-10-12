# Troubleshooting

## Check available formats

```bash
piri --formats
```

## Check native backends

```bash
piri --backends
```

## Diagnose installation

```bash
piri --doctor
```

## Format not available

A format may be recognized but unavailable because its native backend is not installed.

Install the relevant operating-system package and rerun:

```bash
piri --backends
```

## Extraction rejected

Check:

- path traversal
- absolute member paths
- resource limits
- overwrite policy
- special-file restrictions

Use verbose mode:

```bash
piri -v ...
```

## Performance

Check:

```bash
piri --backends
```

and verify whether the selected compressor supports multiple processors.

For serious comparisons, use the benchmark framework instead of assuming that a format is fastest.
