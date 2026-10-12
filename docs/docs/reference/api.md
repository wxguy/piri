# Python API

The stable application interface is `ArchiveEngine`.

Typical usage:

```python
from piri.engine import ArchiveEngine

engine = ArchiveEngine()

result = engine.create("data", "data.tar.zst")
print(result.format)
print(result.elapsed_seconds)
```

Extraction:

```python
result = engine.extract("data.tar.zst", "restore")
```

Integrity:

```python
result = engine.test("data.tar.zst")
```

Detection:

```python
result = engine.detect("data.tar.zst")
```

Listing:

```python
result = engine.list("data.tar.zst")
```

## Operation results

Results can expose information such as:

- format
- backend
- elapsed time
- bytes processed
- member count
- throughput
- CPU time
- RSS telemetry

The API is intended to remain stable while individual native backends evolve.
