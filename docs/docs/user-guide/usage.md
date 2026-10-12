# Usage

piri follows a simple rule:

- **directory input → create an archive**
- **archive input → extract**
- explicit operations such as list and test override the normal action.

## Basic syntax

```text
piri [OPTIONS]
```

The most common options are:

```text
-i, --input PATH
-o, --output PATH
-l, --list
-t, --test
-v, --verbose
-p, --processors N
```

## Archive naming

The output extension is used to select the archive format.

Examples:

```bash
piri -i data/ -o data.tar
piri -i data/ -o data.tar.gz
piri -i data/ -o data.tar.zst
piri -i data/ -o data.zip
piri -i data/ -o data.7z
```

## Automatic extraction

```bash
piri -i backup.tar.zst -o restore/
```

piri detects the format from signatures and extensions.

## Overwrite policy

```bash
piri --overwrite error -i backup.zip -o restore/
piri --overwrite replace -i backup.zip -o restore/
piri --overwrite skip -i backup.zip -o restore/
```

The default is `error`.

## Resource limits

For untrusted archives, limits can be specified:

```bash
piri --max-files 100000      --max-size-gb 20      --max-path-length 4096      -i input.tar.zst -o restore/
```

## Progress

Progress is enabled by default where useful.

Disable it with:

```bash
piri --no-progress ...
```

Progress is written to stderr so normal command output remains script-friendly.
