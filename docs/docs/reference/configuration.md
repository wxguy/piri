# Configuration and Policies

piri exposes safety and metadata policies through the CLI and Python API.

## Overwrite

The default policy is conservative:

```text
error
```

Other options:

```text
replace
skip
```

## Extraction limits

Use limits for untrusted archives:

```bash
--max-files 100000
--max-size-gb 20
--max-path-length 4096
```

## Metadata

Metadata preservation can include portable attributes such as:

- file mode
- modification time

Owner and extended attributes are platform-dependent and should not be assumed portable.

## Progress

Disable progress for automation when required:

```bash
--no-progress
```

## Processor count

```bash
-p 8
```

is a request to use up to eight processors where the selected backend supports it. piri does not artificially parallelize a backend that is inherently serial.
