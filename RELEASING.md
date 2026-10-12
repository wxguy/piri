# Releasing piri

1. Update `piri/__init__.py` and `pyproject.toml` to the release version.
2. Update `CHANGELOG.md`.
3. Run `pytest -q`.
4. Build and verify the standalone installers for each platform.
5. Create a signed/annotated Git tag such as `v1.7.0`.
6. Push the tag to GitHub.
7. The release workflow publishes the standalone artifacts to GitHub Releases.

Never publish a release that has not passed the complete CI matrix.
