# Security

Archive extraction is a security-sensitive operation.

piri applies path and resource policies before writing files.

## Path traversal

Members such as:

```text
../../etc/passwd
```

are rejected.

Absolute paths are also rejected.

## Special files

Unsafe device files, FIFOs and sockets are rejected by the safe extraction policy.

## Resource limits

Limits can protect against archive bombs and unexpectedly large extraction jobs:

```bash
--max-files
--max-size-gb
--max-path-length
```

## Atomic extraction

Use:

```bash
piri --atomic ...
```

when the destination should not be left partially populated after an extraction failure.

## External backends

Optional tools such as `bsdtar`, `7z` and image utilities are treated as security boundaries.

piri validates what it can before invoking an external extractor and does not silently treat arbitrary disk images as ordinary archives.

Report suspected security problems privately according to the project's security policy.
