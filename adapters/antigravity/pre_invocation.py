"""Antigravity's documented ephemeral protocol, not SessionStart."""
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from vibe_wise.restore import restoration


def restore(payload):
    if not isinstance(payload, dict):
        return None
    number, paths = payload.get('invocationNum'), payload.get('workspacePaths')
    if type(number) is not int or number < 0 or not isinstance(paths, list):
        return None
    # No documented active-workspace selector: never silently choose paths[0].
    if len(paths) != 1:
        return None
    try:
        context = restoration(paths[0], ROOT)
    except (OSError, ValueError) as error:
        context = ('VibeWise restoration failed: ' + str(error) +
            '. Explain the restoration problem before continuing active learning. '
            'Do not invent note contents or implementation approval. Use explicit '
            'Learn after repairing the installation or file access. This does not activate learning.')
    if context:
        # Transient context must be delivered on each request. No first-turn cache.
        return {'injectSteps': [{'ephemeralMessage': context}]}


def main():
    try:
        output = restore(json.loads(sys.stdin.read(65536)))
        if output:
            print(json.dumps(output))
    except (OSError, ValueError, TypeError, RecursionError):
        return


if __name__ == '__main__':
    main()
