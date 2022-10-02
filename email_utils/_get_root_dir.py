import os
from pathlib import Path

__all__ = [
    "ROOT_DIR",
]

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
