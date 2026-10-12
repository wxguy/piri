# Integrity Testing

Use:

```bash
piri -t -i archive.tar.zst
```

or:

```bash
piri --test -i archive.zip
```

Integrity testing does **not extract the archive**.

## What is tested?

Depending on the format, piri may:

- validate container structure;
- verify embedded checksums;
- fully consume compressed streams;
- read all archive members;
- invoke a native format-specific integrity checker.

## TAR limitation

Plain TAR does not contain a cryptographic checksum for the payload of each file.

Therefore a structurally valid TAR cannot prove that the original file contents have not been modified.

Compressed TAR formats can additionally detect corruption in the compression stream.

## Exit status

Success:

```text
0
```

Failure:

```text
non-zero
```

This makes `--test` suitable for automated backup validation.
