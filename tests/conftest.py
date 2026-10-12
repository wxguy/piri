import os
from pathlib import Path

# Make subprocess-based CLI tests independent of the directory from which
# pytest was invoked. This mirrors how the package behaves after installation.
os.environ["PYTHONPATH"] = str(Path(__file__).resolve().parents[1]) + os.pathsep + os.environ.get("PYTHONPATH", "")
