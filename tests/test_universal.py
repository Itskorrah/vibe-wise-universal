"""Deterministic installed adapters and sequential handover; no model claims."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vibe_wise.restore import restoration
from vibe_wise.state import state_directory, pending_decisions
from vibe_wise.reset import reset

spec = importlib.util.spec_from_file_location('installer', ROOT / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class UniversalTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='vibe-wise-universal-')
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.project = self.base / 'learner project'
        self.project.mkdir()
        (self.project / '.git').write_text('gitdir: ../worktree-metadata\n')

    def notes(self, paused=False, legacy=False):
        state = self.project / ('.sensible-vibes' if legacy else '.vibe-wise')
        state.mkdir()
        (state / 'profile.md').write_text(
            'Learning mode: ' + ('paused' if paused else 'active') + '\nOnboarding: incomplete\n'
            'Situation: Existing\nOverall programming: Advanced\nRemaining onboarding: preferences\n')
        (state / 'project-map.md').write_text('## Proposed\nStore not confirmed\n')
        (state / 'progress.md').write_text('## Older history\n' + ('Evidence\n' * 30000) +
            '## Pending decision\nStage: awaiting implementation approval\nScope: add one function\n')
        return state

    def bytes_of(self, directory):
        return {p.relative_to(directory).as_posix(): p.read_bytes()
                for p in directory.rglob('*') if p.is_file()}

    def event(self, host, bundle, source='startup', raw=None):
        if host == 'antigravity':
            script = bundle / 'adapters/antigravity/pre_invocation.py'
            payload = {'invocationNum': 0 if source == 'startup' else 45,
                       'workspacePaths': [str(self.project)]}
        else:
            script = bundle / ('hooks/session_start.py' if host == 'claude' else 'adapters/codex/session_start.py')
            payload = {'hook_event_name': 'SessionStart', 'source': source, 'cwd': str(self.project)}
        result = subprocess.run([sys.executable, '-B', str(script)],
            input=raw if raw is not None else json.dumps(payload), cwd=self.base,
            capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout) if result.stdout else None

    def test_all_hosts_preview_install_diagnose_and_remove_without_notes_changes(self):
        for host in installer.HOSTS:
            with self.subTest(host=host):
                original = self.bytes_of(self.project)
                preview = installer.operate(self.project, host, dry_run=True)
                self.assertEqual(preview['status'], 'preview')
                self.assertEqual(self.bytes_of(self.project), original)
                installer.operate(self.project, host)
                self.assertEqual(installer.operate(self.project, host, 'doctor')['status'], 'healthy')
                bundle = self.project / installer.bundle_path(host)
                for name in installer.COMMON:
                    self.assertTrue((bundle / name).is_file(), name)
                installer.operate(self.project, host, 'remove')
                self.assertEqual((self.project / '.git').read_bytes(), original['.git'])

    def test_native_handover_and_full_history_read_instructions(self):
        state = self.notes(legacy=True)
        originals = self.bytes_of(state)
        for host in ('claude', 'codex', 'antigravity'):
            installer.operate(self.project, host)
            bundle = self.project / installer.bundle_path(host)
            for source in ('startup', 'resume', 'clear', 'compact'):
                output = self.event(host, bundle, source)
                text = (output['injectSteps'][0]['ephemeralMessage'] if host == 'antigravity'
                        else output['hookSpecificOutput']['additionalContext'])
                self.assertIn(str(state), text)
                self.assertIn(str(bundle / 'skills/learn/SKILL.md'), text)
                self.assertIn('Search the entire progress.md', text)
                self.assertIn('implementation approval', text)
                self.assertIn('ask only unanswered', text)
                self.assertLess(len(text), 2500)
            self.assertEqual(self.bytes_of(state), originals)
        # OpenCode uses the same read-only bridge, independently of native sessions.
        for host in ('opencode-v1', 'opencode-v2'):
            installer.operate(self.project, host)
            bundle = self.project / installer.bundle_path(host)
            output = subprocess.check_output([sys.executable, '-B', str(bundle / 'scripts/context.py'),
                '--cwd', str(self.project)], cwd=self.base, text=True)
            self.assertIn(str(state), json.loads(output)['context'])
            installer.operate(self.project, host, 'remove')
        self.assertEqual(self.bytes_of(state), originals)

    def test_paused_profile_survives_all_native_events(self):
        state = self.notes(paused=True)
        originals = self.bytes_of(state)
        for host in ('claude', 'codex', 'antigravity'):
            installer.operate(self.project, host)
            for source in ('startup', 'resume', 'clear', 'compact'):
                self.assertIsNone(self.event(host, self.project / installer.bundle_path(host), source))
        self.assertEqual(self.bytes_of(state), originals)

    def test_event_contracts_reject_malformed_and_ambiguous_workspaces(self):
        self.notes()
        for host in ('claude', 'codex', 'antigravity'):
            installer.operate(self.project, host)
            bundle = self.project / installer.bundle_path(host)
            for raw in ('', '{', 'null', '[]', '42', '{"cwd": 3}', '{"workspacePaths": "bad", "invocationNum": 0}'):
                self.assertIsNone(self.event(host, bundle, raw=raw))
            if host == 'antigravity':
                for paths in ([], [str(self.project), str(self.base)]):
                    self.assertIsNone(self.event(host, bundle, raw=json.dumps({'invocationNum': 0, 'workspacePaths': paths})))
                self.assertIsNone(self.event(host, bundle, raw=json.dumps({'invocationNum': True, 'workspacePaths': [str(self.project)]})))
            if host == 'codex':
                self.assertIsNone(self.event(host, bundle, source='fork'))

    def test_installed_hook_command_delivers_protocol_and_registration_is_single(self):
        self.notes()
        for host in ('claude', 'codex', 'antigravity'):
            installer.operate(self.project, host)
            installer.operate(self.project, host)
            bundle = self.project / installer.bundle_path(host)
            if host == 'codex':
                config = json.loads((self.project / '.codex/hooks.json').read_text())
                self.assertEqual(len(config['hooks']['SessionStart']), 1)
            elif host == 'claude':
                config = json.loads((bundle / 'hooks/hooks.json').read_text())
            else:
                config = json.loads((bundle / 'hooks.json').read_text())
            entry = (config['vibe-wise-restoration']['PreInvocation'][0] if host == 'antigravity'
                     else config['hooks']['SessionStart'][0]['hooks'][0])
            payload = ({'workspacePaths': [str(self.project)], 'invocationNum': 0} if host == 'antigravity' else
                       {'hook_event_name': 'SessionStart', 'source': 'compact', 'cwd': str(self.project)})
            result = subprocess.run(entry['command'], shell=True, cwd=self.base,
                input=json.dumps(payload), text=True, capture_output=True, timeout=5)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(result.stdout))

    def test_missing_resources_and_nonregular_notes_are_diagnosable(self):
        state = self.notes()
        installer.operate(self.project, 'portable')
        bundle = self.project / installer.bundle_path('portable')
        (bundle / 'skills/learn/behavior.md').unlink()
        self.assertEqual(installer.operate(self.project, 'portable', 'doctor')['status'], 'attention')
        with self.assertRaisesRegex(ValueError, 'Missing'):
            restoration(str(self.project), bundle)
        (bundle / 'skills/learn/behavior.md').write_bytes((ROOT / 'skills/learn/behavior.md').read_bytes())
        (state / 'progress.md').unlink()
        (state / 'progress.md').mkdir()
        with self.assertRaisesRegex(ValueError, 'non-regular'):
            restoration(str(self.project), bundle)

    def test_native_missing_resource_failure_reaches_model_protocol(self):
        self.notes()
        for host in ('claude', 'codex', 'antigravity'):
            installer.operate(self.project, host)
            bundle = self.project / installer.bundle_path(host)
            (bundle / 'skills/learn/behavior.md').unlink()
            result = self.event(host, bundle)
            context = (result['injectSteps'][0]['ephemeralMessage'] if host == 'antigravity'
                       else result['hookSpecificOutput']['additionalContext'])
            self.assertIn('restoration failed', context)
            self.assertIn('Do not invent', context)

    def test_relocated_bundle_runs_without_original_source(self):
        state = self.notes()
        for host in ('claude', 'codex', 'antigravity', 'portable'):
            installer.operate(self.project, host)
            bundle = self.project / installer.bundle_path(host)
            relocated = self.base / ('relocated-' + host)
            shutil.move(bundle, relocated)
            result = subprocess.run([sys.executable, '-B', str(relocated / 'scripts/context.py'),
                '--cwd', str(self.project)], cwd=self.base, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = json.loads(result.stdout)['context']
            self.assertIn(str(relocated / 'skills/learn/SKILL.md'), text)
            preview = json.loads(subprocess.check_output([sys.executable, '-B',
                str(relocated / 'skills/reset/reset.py'), '--cwd', str(self.project)], text=True))
            self.assertEqual(preview['state'], str(state))

    def test_update_and_removal_preserve_user_config_and_notes(self):
        state = self.notes()
        originals = self.bytes_of(state)
        (self.project / 'AGENTS.md').write_text('User instructions\n')
        config_dir = self.project / '.codex'
        config_dir.mkdir()
        group = {'matcher': 'startup', 'hooks': [{'type': 'command', 'command': 'user-command'}]}
        (config_dir / 'hooks.json').write_text(json.dumps({'description': 'Keep', 'hooks': {'SessionStart': [group]}}))
        installer.operate(self.project, 'codex', instructions=True)
        with (self.project / 'AGENTS.md').open('a') as stream:
            stream.write('Later user instructions\n')
        installer.operate(self.project, 'codex', 'update')
        config = json.loads((config_dir / 'hooks.json').read_text())
        self.assertEqual(len(config['hooks']['SessionStart']), 2)
        self.assertEqual(config['hooks']['SessionStart'][0], group)
        installer.operate(self.project, 'codex', 'remove')
        config = json.loads((config_dir / 'hooks.json').read_text())
        self.assertEqual(config['hooks']['SessionStart'], [group])
        self.assertEqual(config['description'], 'Keep')
        text = (self.project / 'AGENTS.md').read_text()
        self.assertIn('User instructions', text)
        self.assertIn('Later user instructions', text)
        self.assertNotIn(installer.BEGIN, text)
        self.assertEqual(self.bytes_of(state), originals)

    def test_modified_owned_file_or_block_prevents_any_update_or_removal(self):
        installer.operate(self.project, 'portable', instructions=True)
        bundle = self.project / installer.bundle_path('portable')
        (bundle / 'LEARN.md').write_text('My edited skill')
        original = self.bytes_of(self.project)
        for action in ('update', 'remove'):
            with self.assertRaisesRegex(ValueError, 'Owned file changed'):
                installer.operate(self.project, 'portable', action)
        self.assertEqual(self.bytes_of(self.project), original)

    def test_unowned_files_and_mutually_exclusive_plugins_are_preserved(self):
        directory = self.project / '.opencode/plugins'
        directory.mkdir(parents=True)
        (directory / 'user.ts').write_text('Keep plugin')
        installer.operate(self.project, 'opencode-v1')
        with self.assertRaisesRegex(ValueError, 'Remove'):
            installer.operate(self.project, 'opencode-v2')
        installer.operate(self.project, 'opencode-v1', 'remove')
        self.assertEqual((directory / 'user.ts').read_text(), 'Keep plugin')
        installer.operate(self.project, 'opencode-v2')

    def test_failed_install_rolls_back_owned_files_and_existing_config(self):
        (self.project / 'AGENTS.md').write_text('Keep me')
        original = self.bytes_of(self.project)
        real = installer.atomic_write
        def fail(path, data):
            if path.name == 'python.json':
                raise OSError('injected write failure')
            real(path, data)
        with patch.object(installer, 'atomic_write', fail):
            with self.assertRaisesRegex(ValueError, 'Installation failed'):
                installer.operate(self.project, 'portable', instructions=True)
        self.assertEqual(self.bytes_of(self.project), original)

    def test_missing_source_invalid_destination_and_unowned_collision_write_nothing(self):
        for project in ('relative', self.base / 'missing'):
            with self.assertRaises(ValueError):
                installer.operate(project, 'portable')
        empty = self.base / 'empty-source'
        empty.mkdir()
        with self.assertRaisesRegex(ValueError, 'Missing bundle'):
            installer.operate(self.project, 'portable', source=empty)
        self.assertEqual(list(self.project.iterdir()), [self.project / '.git'])
        target = self.project / installer.bundle_path('portable')
        target.mkdir(parents=True)
        (target / 'LICENSE').write_text('User file')
        before = self.bytes_of(self.project)
        with self.assertRaisesRegex(ValueError, 'Unowned'):
            installer.operate(self.project, 'portable')
        self.assertEqual(self.bytes_of(self.project), before)

    def test_manual_codex_update_does_not_silently_register_hooks(self):
        installer.operate(self.project, 'codex', manual=True)
        installer.operate(self.project, 'codex', 'update')
        self.assertFalse((self.project / '.codex/hooks.json').exists())
        self.assertFalse(installer.operate(self.project, 'codex', 'doctor')['capabilities']['automatic_restoration_configured'])

    def test_installed_reset_keeps_snapshot_scope_and_backup(self):
        state = self.notes()
        originals = self.bytes_of(state)
        installer.operate(self.project, 'antigravity')
        bundle = self.project / installer.bundle_path('antigravity')
        command = [sys.executable, '-B', str(bundle / 'skills/reset/reset.py'), '--cwd', str(self.project)]
        preview = json.loads(subprocess.check_output(command, text=True))
        self.assertEqual(self.bytes_of(state), originals)
        (state / 'progress.md').write_text('Changed notes\n')
        stale = subprocess.run(command + ['--confirm', preview['confirmation']], capture_output=True, text=True)
        self.assertEqual(stale.returncode, 1)
        self.assertFalse((state / 'backups').exists())
        preview = json.loads(subprocess.check_output(command, text=True))
        result = json.loads(subprocess.check_output(command + ['--confirm', preview['confirmation']], text=True))
        backup = Path(result['backup'])
        self.assertEqual((backup / 'progress.md').read_text(), 'Changed notes\n')
        self.assertIn('Onboarding: incomplete', (state / 'profile.md').read_text())
        self.assertTrue((self.project / '.git').is_file())

    def test_pending_index_searches_full_large_history_and_returns_complete_sections(self):
        state = self.notes()
        with (state / 'progress.md').open('a') as stream:
            stream.write('Tradeoffs: keep membership independent.\n\n### Proposed additions\nNo approval.\n'
                         '## Past implemented work\nAlready implemented\n'
                         '## Another topic\nStage: awaiting reasoning\nComplete reasoning scope\n')
        original = self.bytes_of(state)
        pending = pending_decisions(state / 'progress.md')
        self.assertEqual(len(pending), 2)
        self.assertGreater(pending[0]['start_line'], 30000)
        self.assertIn('### Proposed additions\nNo approval.', pending[0]['text'])
        self.assertNotIn('Already implemented', pending[0]['text'])
        self.assertIn('Complete reasoning scope', pending[1]['text'])
        self.assertEqual(self.bytes_of(state), original)
        installer.operate(self.project, 'portable')
        output = json.loads(subprocess.check_output([sys.executable, '-B',
            str(self.project / installer.bundle_path('portable') / 'scripts/context.py'),
            '--cwd', str(self.project), '--pending'], text=True))
        self.assertEqual(output['pending'], pending)

    def test_changed_instruction_block_is_preserved_on_removal(self):
        installer.operate(self.project, 'portable', instructions=True)
        path = self.project / 'AGENTS.md'
        path.write_text(path.read_text().replace('Installation is not activation.', 'My custom rule.'))
        original = self.bytes_of(self.project)
        with self.assertRaisesRegex(ValueError, 'changed VibeWise'):
            installer.operate(self.project, 'portable', 'remove')
        self.assertEqual(self.bytes_of(self.project), original)

    def test_changed_hook_fragment_is_preserved_on_update(self):
        installer.operate(self.project, 'codex')
        path = self.project / '.codex/hooks.json'
        config = json.loads(path.read_text())
        config['hooks']['SessionStart'][0]['hooks'][0]['command'] = 'My custom hook'
        path.write_text(json.dumps(config))
        original = self.bytes_of(self.project)
        with self.assertRaisesRegex(ValueError, 'fragment changed'):
            installer.operate(self.project, 'codex', 'update')
        self.assertEqual(self.bytes_of(self.project), original)

    def test_removal_preserves_unowned_bundle_files(self):
        installer.operate(self.project, 'portable')
        extra = self.project / installer.bundle_path('portable') / 'user-file.md'
        extra.write_text('Keep this')
        installer.operate(self.project, 'portable', 'remove')
        self.assertEqual(extra.read_text(), 'Keep this')

    def test_forged_manifest_cannot_remove_another_project(self):
        installer.operate(self.project, 'portable')
        outside = self.base / 'other-project.txt'
        outside.write_text('Preserve')
        path = installer.manifest_path(self.project, 'portable')
        manifest = json.loads(path.read_text())
        manifest['files']['../other-project.txt'] = installer.digest(outside.read_bytes())
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'Invalid managed path'):
            installer.operate(self.project, 'portable', 'remove')
        self.assertEqual(outside.read_text(), 'Preserve')

    def test_forged_manifest_cannot_claim_application_or_learner_notes(self):
        state = self.notes()
        installer.operate(self.project, 'portable')
        application = self.project / 'app.py'
        application.write_text('Keep application')
        path = installer.manifest_path(self.project, 'portable')
        original = json.loads(path.read_text())
        for file in (application, state / 'profile.md'):
            manifest = json.loads(json.dumps(original))
            manifest['files'][file.relative_to(self.project).as_posix()] = installer.digest(file.read_bytes())
            path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'host allowlist'):
                installer.operate(self.project, 'portable', 'remove')
            self.assertTrue(file.is_file())

    def test_missing_interpreter_is_rejected_before_writes(self):
        with self.assertRaisesRegex(ValueError, 'interpreter not found'):
            installer.operate(self.project, 'codex', python='vibe-wise-nonexistent-python')
        self.assertEqual(list(self.project.iterdir()), [self.project / '.git'])

    def test_symlinked_destination_and_source_are_rejected(self):
        target = self.base / 'outside'
        target.mkdir()
        link = self.project / '.vibe-wise-bundle'
        try:
            link.symlink_to(target, target_is_directory=True)
        except OSError as error:
            if getattr(error, 'winerror', None) == 1314:
                self.skipTest('Windows symlink privilege unavailable; exercised in Unix CI')
            raise
        with self.assertRaisesRegex(ValueError, 'linked'):
            installer.operate(self.project, 'portable')
        self.assertEqual(list(target.iterdir()), [])
        link.unlink()
        source = self.base / 'source-copy'
        shutil.copytree(ROOT / 'skills', source / 'skills')
        (source / 'LICENSE').symlink_to(ROOT / 'LICENSE')
        with self.assertRaisesRegex(ValueError, 'linked'):
            installer.operate(self.project, 'portable', source=source)

    @unittest.skipUnless(os.name == 'nt', 'Windows-specific junction regression')
    def test_windows_junction_rejected_for_state_and_installation(self):
        # Junction creation does not require Windows symlink privileges.
        outside = self.base / 'outside-junction'
        outside.mkdir()
        link = self.project / '.vibe-wise'
        def junction(path):
            quoted_link = str(path).replace("'", "''")
            quoted_target = str(outside).replace("'", "''")
            result = subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                f"New-Item -ItemType Junction -Path '{quoted_link}' -Target '{quoted_target}'"],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        junction(link)
        self.assertIsNone(state_directory(self.project))
        self.assertEqual(reset(self.project)['status'], 'no_notes')
        junction(self.project / '.vibe-wise-bundle')
        with self.assertRaisesRegex(ValueError, 'linked'):
            installer.operate(self.project, 'portable')
        self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
