"""Documented Codex SessionStart policy, separate from Claude."""
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from vibe_wise.restore import restoration


def restore(payload):
    if not isinstance(payload, dict) or payload.get('hook_event_name') != 'SessionStart':
        return None
    if payload.get('source') not in ('startup', 'resume', 'clear', 'compact'):
        return None
    try:
        context = restoration(payload.get('cwd'), ROOT)
    except (OSError, ValueError) as error:
        context = ('VibeWise restoration failed: ' + str(error) +
            '. Explain the restoration problem before continuing active learning. '
            'Do not invent note contents or implementation approval. Use explicit '
            'Learn after repairing the installation or file access. This does not activate learning.')
    if context:
        return {'hookSpecificOutput': {'hookEventName': 'SessionStart',
                                     'additionalContext': context}}


def main():
    try:
        output = restore(json.loads(sys.stdin.read(65536)))
        if output:
            print(json.dumps(output))
    except (OSError, ValueError, TypeError, RecursionError):
        return


if __name__ == '__main__':
    main()
