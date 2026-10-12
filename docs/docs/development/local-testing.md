---
id: local-testing
title: Local Testing Before GitHub
description: Test piri locally before committing or pushing changes.
---

# Local testing before GitHub

The recommended workflow is to test piri locally before committing changes or pushing them to GitHub.

## Python environment

Install [uv](https://docs.astral.sh/uv/) before setting up the environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
uv sync --extra test
```

On Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
uv sync --extra test
```

## Run the tests

```bash
uv run pytest -q
python -m compileall -q piri
```

## Test the command line

```bash
uv run piri --version
uv run piri --formats
uv run piri --backends
uv run piri --doctor
```

## Test a real archive round trip

```bash
mkdir -p /tmp/piri-test/input
printf 'piri test\n' > /tmp/piri-test/input/test.txt
piri -i /tmp/piri-test/input -o /tmp/piri-test/test.tar.zst
piri -t /tmp/piri-test/test.tar.zst
piri -i /tmp/piri-test/test.tar.zst -o /tmp/piri-test/output
cat /tmp/piri-test/output/test.txt
```

## Test the documentation site

```bash
cd docs
npm install
npm start
```

Open the local URL shown by Docusaurus. For a production build:

```bash
npm run build
npm run serve
```

## Check Git changes

Before committing:

```bash
git status
git diff
git diff --check
```

Use a feature branch rather than committing directly to `main`:

```bash
git checkout -b feature/my-change
git add .
git commit -m "Describe the change"
git push -u origin feature/my-change
```

Review the branch and CI results before merging it into `main`.
