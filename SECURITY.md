# Security Policy

## Reporting a vulnerability

Please do not disclose an archive traversal, archive-bomb, symlink or command
execution vulnerability in a public issue. Contact the project maintainer
privately with a minimal reproducer and affected version.

## Security design

piri treats archive extraction as untrusted input. It validates paths, rejects
unsafe special files where supported, applies resource limits, and provides
explicit overwrite policies. Native third-party backends are only advertised
with the safety capabilities they can actually guarantee.

Users should keep native archive utilities updated because piri delegates
format-specific parsing to them where appropriate.
