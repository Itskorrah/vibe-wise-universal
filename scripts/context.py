"""Portable/OpenCode read-only JSON bridge, independent of the process cwd."""
import argparse
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vibe_wise.restore import restoration
from vibe_wise.state import pending_decisions, state_directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', required=True)
    parser.add_argument('--pending', action='store_true', help='Read complete canonical pending sections (still search legacy history)')
    args = parser.parse_args()
    try:
        context = restoration(args.cwd, ROOT)
        result = {'context': context}
        if args.pending:
            if not Path(args.cwd).is_absolute() or not Path(args.cwd).is_dir():
                raise ValueError('Use an existing absolute project directory.')
            state = state_directory(Path(args.cwd).resolve())
            result['pending'] = pending_decisions(state / 'progress.md') if state and (state / 'progress.md').exists() else []
        print(json.dumps(result))
        return 0
    except (OSError, ValueError) as error:
        print(json.dumps({'error': str(error)}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
