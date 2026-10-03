"""Compatibility entry point for the original Claude reset command."""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from vibe_wise.reset import *
if __name__ == "__main__":
    sys.exit(main())
