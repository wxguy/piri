# Release Process

Releases should be reproducible and validated before publication.

## Checklist

- Update version metadata.
- Update `CHANGELOG.md`.
- Run the complete test suite.
- Build the standalone installers and archives.
- Install a standalone build into a clean environment.
- Verify `piri --version`.
- Run format/backend discovery.
- Run representative round-trip tests.
- Run integrity tests.
- Build the documentation.
- Review the generated artifacts.
- Create a Git tag.
- Publish the standalone installers and archives to the GitHub release.

Never publish an artifact that has not passed the clean-install test.
