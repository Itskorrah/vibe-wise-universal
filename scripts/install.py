"""Preview, install, update, diagnose or remove project-local owned resources."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
from vibe_wise.state import is_link

HOSTS = ('claude', 'codex', 'opencode-v1', 'opencode-v2', 'antigravity',
         'antigravity-manual', 'portable')
COMMON = (
    'LICENSE', 'skills/learn/SKILL.md', 'skills/learn/behavior.md',
    'skills/learn/onboarding.md', 'skills/learn/state-templates.md',
    'skills/reset/SKILL.md', 'skills/reset/reset.py',
    'skills/learn/agents/openai.yaml', 'skills/reset/agents/openai.yaml',
    'vibe_wise/__init__.py', 'vibe_wise/state.py', 'vibe_wise/restore.py',
    'vibe_wise/reset.py', 'scripts/context.py',
)
EXTRA = {
    'claude': ('.claude-plugin/plugin.json', 'hooks/session_start.py', 'hooks/hooks.json'),
    'codex': ('plugin.json', '.codex-plugin/plugin.json', 'adapters/codex/hooks.json', 'adapters/codex/session_start.py'),
    'antigravity': ('plugin.json', 'hooks.json', 'adapters/antigravity/pre_invocation.py'),
    'opencode-v1': ('adapters/opencode-v1/plugin.ts', 'adapters/opencode-common/bridge.mjs'),
    'opencode-v2': ('adapters/opencode-v2/setup.ts', 'adapters/opencode-common/bridge.mjs'),
}
BEGIN = '<!-- vibe-wise:managed:start -->'
END = '<!-- vibe-wise:managed:end -->'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(project, relative):
    """Validate every component before resolving links, including junctions."""
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts or not relative.parts:
        raise ValueError('Invalid managed path: ' + str(relative))
    candidate = project
    for part in relative.parts:
        candidate /= part
        if is_link(candidate):
            raise ValueError('Refusing linked destination: ' + str(candidate))
    candidate.resolve().relative_to(project)
    return candidate


def project_path(project):
    project = Path(project)
    if not project.is_absolute() or not project.is_dir():
        raise ValueError('Use an existing absolute target project directory.')
    for candidate in (project, *project.parents):
        if is_link(candidate):
            raise ValueError('Refusing linked project path: ' + str(candidate))
    return project.resolve()


def command(arguments):
    # Reject cmd.exe expansion rather than risking a silently changed path.
    if os.name == 'nt':
        if any(any(char in str(arg) for char in '%!\r\n') for arg in arguments):
            raise ValueError('Windows hook paths cannot contain %, ! or newlines.')
        return subprocess.list2cmdline([str(arg) for arg in arguments])
    return shlex.join([str(arg) for arg in arguments])


def bundle_path(host):
    return Path('.agents/plugins/vibe-wise') if host == 'antigravity' else Path('.vibe-wise-bundle') / host


def manifest_path(project, host):
    return safe_path(project, Path('.vibe-wise-bundle') / (host + '.manifest.json'))


def load_manifest(project, host):
    path = manifest_path(project, host)
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding='utf-8'))
    if value.get('schema') != 1 or value.get('host') != host:
        raise ValueError('Unrecognized ownership manifest: ' + str(path))
    root = bundle_path(host)
    allowed = {(root / name).as_posix() for name in COMMON + EXTRA.get(host, ())}
    allowed.add((root / 'python.json').as_posix())
    if host in ('codex', 'antigravity-manual'):
        for name in ('learn', 'reset'):
            directory = Path('.agents/skills') / ('vibe-wise-' + name)
            allowed.update(((directory / 'SKILL.md').as_posix(),
                            (directory / 'agents/openai.yaml').as_posix()))
    if host == 'opencode-v1':
        allowed.update(('.opencode/plugins/vibe-wise.ts', '.opencode/commands/vibe-wise-learn.md',
                        '.opencode/commands/vibe-wise-reset.md'))
    if host == 'opencode-v2':
        allowed.update(('.opencode/plugins/vibe-wise/index.ts', '.opencode/plugins/vibe-wise/package.json'))
    if host == 'portable':
        allowed.update(((root / 'LEARN.md').as_posix(), (root / 'RESET.md').as_posix()))
    for name in value['files']:
        safe_path(project, name)
        if name not in allowed:
            raise ValueError('Manifest claims a file outside the host allowlist: ' + name)
    return value


def skill_wrapper(name, guide):
    return (
        f'---\nname: vibe-wise-{name}\n'
        f'description: Use only for an explicit VibeWise {name} request.\n'
        'disable-model-invocation: true\n---\n\n'
        'Discovery alone never starts or resumes learning. Stay in the main conversation.\n'
        f'Only when explicitly invoked, read [canonical {name} guide]({guide}) and follow it.\n'
        'Resolve resources from the guide, not the project cwd. Text questions are the\n'
        'fallback when native question tools are unavailable or not permitted.\n'
    ).encode()


def payload(project, host, source=SOURCE, python=None, instructions=False):
    python = python or sys.executable
    if not shutil.which(python):
        raise ValueError('Python interpreter not found: ' + str(python))
    root = bundle_path(host)
    files = {}
    for relative in COMMON + EXTRA.get(host, ()):
        origin = safe_path(source.resolve(), relative)
        if not origin.is_file():
            raise ValueError('Missing bundle resource: ' + str(origin))
        files[(root / relative).as_posix()] = origin.read_bytes()
    files[(root / 'python.json').as_posix()] = json.dumps({'executable': python}).encode()
    if host in ('claude', 'codex', 'antigravity'):
        # Concrete interpreter and installed script paths avoid shell-specific env
        # expansion and source-checkout dependencies. No user configuration edited.
        path = {'claude': 'hooks/hooks.json', 'codex': 'adapters/codex/hooks.json',
                'antigravity': 'hooks.json'}[host]
        config = json.loads(files[(root / path).as_posix()])
        if host == 'antigravity':
            manifest_name = (root / 'plugin.json').as_posix()
            native_manifest = json.loads(files[manifest_name])
            native_manifest.pop('extensions', None)
            files[manifest_name] = json.dumps(native_manifest, indent=2).encode()
        script = {'claude': 'hooks/session_start.py', 'codex': 'adapters/codex/session_start.py',
                  'antigravity': 'adapters/antigravity/pre_invocation.py'}[host]
        entry = (config['vibe-wise-restoration']['PreInvocation'][0] if host == 'antigravity'
                 else config['hooks']['SessionStart'][0]['hooks'][0])
        entry['command'] = command([python, safe_path(project, root / script)])
        files[(root / path).as_posix()] = json.dumps(config, indent=2).encode()
    if host in ('codex', 'antigravity-manual'):
        for name in ('learn', 'reset'):
            directory = Path('.agents/skills') / ('vibe-wise-' + name)
            target = os.path.relpath(project / root / 'skills' / name / 'SKILL.md', project / directory).replace('\\', '/')
            files[(directory / 'SKILL.md').as_posix()] = skill_wrapper(name, target)
            files[(directory / 'agents/openai.yaml').as_posix()] = (source / 'skills' / name / 'agents/openai.yaml').read_bytes()
    if host == 'opencode-v1':
        files['.opencode/plugins/vibe-wise.ts'] = (
            'export { default } from "../../.vibe-wise-bundle/opencode-v1/adapters/opencode-v1/plugin.ts";\n'
        ).encode()
        for name in ('learn', 'reset'):
            files[f'.opencode/commands/vibe-wise-{name}.md'] = (
                f'---\ndescription: Explicit VibeWise {name}\nsubtask: false\n---\n'
                f'Explicitly invoke VibeWise {name} in this conversation. $ARGUMENTS\n'
                'The VibeWise plugin will attach the installed canonical guide path.\n'
            ).encode()
    if host == 'opencode-v2':
        files['.opencode/plugins/vibe-wise/index.ts'] = (
            'import type { Plugin } from "@opencode/plugin";\n'
            'import { makeSetup } from "../../../.vibe-wise-bundle/opencode-v2/adapters/opencode-v2/setup.ts";\n'
            'export default { id: "vibe-wise", setup: makeSetup() } satisfies Plugin.Plugin;\n'
        ).encode()
        files['.opencode/plugins/vibe-wise/package.json'] = json.dumps({
            'private': True, 'type': 'module'
        }).encode()
    if host == 'portable':
        files[(root / 'LEARN.md').as_posix()] = skill_wrapper('learn', 'skills/learn/SKILL.md')
        files[(root / 'RESET.md').as_posix()] = skill_wrapper('reset', 'skills/reset/SKILL.md')
    block = None
    if instructions:
        block = (f'{BEGIN}\nVibeWise is installed at `{root.as_posix()}`. Installation is not activation.\n'
                 'When explicitly asked to Learn/resume, read its `skills/learn/SKILL.md`.\n'
                 'When explicitly asked to Reset, read its `skills/reset/SKILL.md`; preview and confirm.\n'
                 'On startup, resume or compaction, check nearest project learning notes inside the\n'
                 'Git/worktree boundary. Restore active notes through `scripts/context.py --cwd`\n'
                 'and read the returned guides, profile, map and complete pending progress sections.\n'
                 'Paused mode stays paused. Restart and agent switching never authorise code.\n'
                 f'{END}').encode()
    return files, block


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.vibe-wise-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def instruction_edit(project, previous, desired):
    path = safe_path(project, 'AGENTS.md')
    data = path.read_bytes() if path.exists() else b''
    begin, end = BEGIN.encode(), END.encode()
    if begin in data or end in data:
        if data.count(begin) != 1 or data.count(end) != 1:
            raise ValueError('Ambiguous VibeWise managed instruction block.')
        start, stop = data.index(begin), data.index(end) + len(end)
        if stop <= start or not previous or digest(data[start:stop]) != previous:
            raise ValueError('Unowned or changed VibeWise instruction block; preserve it.')
        return data[:start] + (desired or b'') + data[stop:]
    if previous:
        raise ValueError('Owned instruction block is missing; preserve user edits.')
    if desired:
        return data + (b'\n' if data and not data.endswith(b'\n') else b'') + desired + b'\n'
    return data


def codex_hooks_edit(project, previous, desired):
    path = safe_path(project, '.codex/hooks.json')
    value = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    hooks = value.setdefault('hooks', {})
    groups = hooks.setdefault('SessionStart', [])
    owned = [group for group in groups if any(hook.get('statusMessage') == 'VibeWise managed restoration' for hook in group.get('hooks', []))]
    if len(owned) > 1:
        raise ValueError('Duplicate VibeWise registration; resolve before installing.')
    if owned:
        if not previous or digest(json.dumps(owned[0], sort_keys=True).encode()) != previous:
            raise ValueError('VibeWise hook fragment changed or is not owned.')
        groups.remove(owned[0])
    elif previous:
        raise ValueError('Owned hook registration missing.')
    if desired:
        groups.append(desired)
    return json.dumps(value, indent=2).encode()


def runtime_report(project, host):
    names = {'claude': ('claude',), 'codex': ('codex',),
             'opencode-v1': ('opencode',), 'opencode-v2': ('opencode',),
             'antigravity': ('agy', 'antigravity'), 'antigravity-manual': ('agy', 'antigravity')}
    available = {name: shutil.which(name) for name in names.get(host, ())}
    missing = []
    if available and not any(available.values()):
        missing.append('Host CLI not found on PATH; GUI availability is not detected.')
    config = safe_path(project, bundle_path(host) / 'python.json')
    python = None
    if config.is_file():
        try:
            python = json.loads(config.read_text())['executable']
            if not isinstance(python, str) or not shutil.which(python):
                missing.append('Installed Python executable is unavailable: ' + str(python))
        except (ValueError, KeyError, OSError):
            missing.append('Installed interpreter configuration is unreadable or malformed.')
    if host == 'opencode-v2':
        missing.append('V2 plugin descriptor loading must be verified in OpenCode; type imports have no runtime dependency.')
    if host in ('codex', 'claude', 'antigravity'):
        missing.append('Hook execution/trust and model delivery require host-side verification.')
    if host in ('portable', 'antigravity-manual'):
        missing.append('Automatic lifecycle restoration unavailable; explicitly resume after context loss.')
    return {'executables': available, 'python': python, 'missing_or_unverified_capabilities': missing}


def operate(project, host, action='install', dry_run=False, source=SOURCE,
            python=None, instructions=False, manual=None):
    if host not in HOSTS:
        raise ValueError('Unknown host.')
    project = project_path(project)
    old = load_manifest(project, host)
    manual = (old or {}).get('manual', False) if manual is None else manual
    if manual and host != 'codex':
        raise ValueError('--manual applies only to Codex; use antigravity-manual for Google fallback.')
    if action == 'doctor':
        issues = []
        if not old:
            issues.append('No installation ownership manifest.')
        else:
            for name, expected in old['files'].items():
                path = safe_path(project, name)
                if not path.is_file() or digest(path.read_bytes()) != expected:
                    issues.append('Missing or modified resource: ' + name)
            try:
                if old.get('instructions'):
                    instruction_edit(project, old['instructions'], None)
                if old.get('hook'):
                    codex_hooks_edit(project, old['hook'], None)
            except (ValueError, OSError) as error:
                issues.append(str(error))
        return {'status': 'healthy' if not issues else 'attention', 'host': host,
                'issues': issues, 'files': list(old['files']) if old else [],
                'runtime': runtime_report(project, host),
                'capabilities': {
                    'state_format': 'Local Markdown; dependable host file access required.',
                    'concurrent_editing': False,
                    'automatic_restoration_configured': bool(old and old.get('automatic')),
                    'hook_trust': 'Host approval required; never changed by installer.',
                    'live_verification': 'See docs/compatibility.md; deterministic checks are not model evaluations.'}}
    if action == 'update' and not old:
        raise ValueError('Not installed; use install first.')
    if action == 'install' and old:
        action = 'update'  # idempotent registration, with the same ownership checks
    if action == 'remove' and not old:
        return {'status': 'not_installed', 'host': host}
    # V1/V2 discover the same plugin identity; prevent loading both implementations.
    exclusive = {'opencode-v1': 'opencode-v2', 'opencode-v2': 'opencode-v1',
                 'antigravity': 'antigravity-manual', 'antigravity-manual': 'antigravity'}
    if action != 'remove' and host in exclusive and load_manifest(project, exclusive[host]):
        raise ValueError('Remove ' + exclusive[host] + ' before installing ' + host + '.')
    for name, expected in (old or {}).get('files', {}).items():
        path = safe_path(project, name)
        if not path.is_file() or digest(path.read_bytes()) != expected:
            raise ValueError('Owned file changed; preserve edits and resolve first: ' + str(path))
    files, block = ({}, None) if action == 'remove' else payload(
        project, host, Path(source), python, instructions or bool(old and old.get('instructions')))
    for name in files:
        path = safe_path(project, name)
        if path.exists() and name not in (old or {}).get('files', {}):
            raise ValueError('Unowned destination exists; nothing overwritten: ' + str(path))
    edits = {}
    if block or old and old.get('instructions'):
        edits['AGENTS.md'] = instruction_edit(project, (old or {}).get('instructions'), block)
    group = None
    if host == 'codex' and action != 'remove' and not manual:
        config = json.loads(files[(bundle_path(host) / 'adapters/codex/hooks.json').as_posix()])
        group = config['hooks']['SessionStart'][0]
        group['hooks'][0]['statusMessage'] = 'VibeWise managed restoration'
    if group or old and old.get('hook'):
        edits['.codex/hooks.json'] = codex_hooks_edit(project, (old or {}).get('hook'), group)
    result = {'status': 'preview' if dry_run else action, 'host': host, 'project': str(project),
              'bundle': str(project / bundle_path(host)), 'files': list(files),
              'remove': [name for name in (old or {}).get('files', {}) if name not in files],
              'configuration': list(edits), 'manual': manual,
              'next': 'Restart host; review hook trust if applicable. Invoke Learn explicitly.'}
    if dry_run:
        return result
    changes = dict(files, **edits)
    for name in result['remove']:
        changes[name] = None
    manifest = {'schema': 1, 'host': host, 'manual': manual, 'files': {name: digest(data) for name, data in files.items()},
                'instructions': digest(block) if block else None,
                'hook': digest(json.dumps(group, sort_keys=True).encode()) if group else None,
                'automatic': not manual and host in ('claude', 'codex', 'opencode-v1', 'opencode-v2', 'antigravity')}
    location = manifest_path(project, host).relative_to(project).as_posix()
    changes[location] = None if action == 'remove' else json.dumps(manifest, indent=2).encode()
    originals = {name: safe_path(project, name).read_bytes() if safe_path(project, name).is_file() else None
                 for name in changes}
    completed = []
    try:
        for name, data in changes.items():
            path = safe_path(project, name)
            if data is None:
                if path.exists():
                    path.unlink()
            else:
                atomic_write(path, data)
            completed.append(name)
    except (OSError, ValueError) as error:
        failures = []
        for name in reversed(completed):
            try:
                path = safe_path(project, name)
                if originals[name] is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, originals[name])
            except (OSError, ValueError) as rollback:
                failures.append(str(rollback))
        raise ValueError(f'Installation failed: {error}. Rollback failures: {failures}') from error
    # Remove only empty directories below owned roots. Never recursive-delete a project.
    if action == 'remove':
        for name in (old or {}).get('files', {}):
            parent = safe_path(project, name).parent
            while parent != project:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('install', 'update', 'doctor', 'remove'))
    parser.add_argument('--host', choices=HOSTS, required=True)
    parser.add_argument('--project', required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--python', help='Python 3 executable for installed native hooks')
    parser.add_argument('--instructions', action='store_true', help='Managed restoration block in target AGENTS.md')
    parser.add_argument('--manual', action='store_true', default=None, help='Codex skills only; no lifecycle registration')
    args = parser.parse_args()
    try:
        result = operate(args.project, args.host, args.action, args.dry_run,
                         python=args.python, instructions=args.instructions, manual=args.manual)
        print(json.dumps(result, indent=2))
        return 1 if result['status'] == 'attention' else 0
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'error', 'message': str(error)}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
