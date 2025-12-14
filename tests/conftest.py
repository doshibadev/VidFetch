import os
import sys


# Ensure `src` is on sys.path so `import core` works when running tests
ROOT = os.path.dirname(os.path.dirname(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
