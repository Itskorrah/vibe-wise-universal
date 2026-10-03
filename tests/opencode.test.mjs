import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { makePlugin } from '../adapters/opencode-v1/plugin.ts';
import { makeSetup } from '../adapters/opencode-v2/setup.ts';
import { contextFor } from '../adapters/opencode-common/bridge.mjs';

test('V1 looks up the relevant session and delivers system/compaction context once per request', async () => {
  const calls = [];
  const plugin = await makePlugin(async directory => { calls.push(directory); return `Restore ${directory}`; })({
    directory: '/wrong-load-directory', client: { session: { get: async ({ path }) => ({ data: { directory: `/${path.id}` } }) } },
  });
  const output = { system: ['Keep user system'] };
  await plugin['experimental.chat.system.transform']({ sessionID: 'repo-a' }, output);
  await plugin['experimental.chat.system.transform']({ sessionID: 'repo-a' }, output);
  assert.deepEqual(output.system, ['Keep user system', 'Restore /repo-a']);
  const afterCompaction = { system: [] };
  await plugin['experimental.chat.system.transform']({ sessionID: 'repo-a' }, afterCompaction);
  assert.deepEqual(afterCompaction.system, ['Restore /repo-a']);
  const compact = { context: [] };
  await plugin['experimental.session.compacting']({ sessionID: 'repo-b' }, compact);
  assert.deepEqual(compact.context, ['Restore /repo-b']);
  const missing = { system: [] };
  await plugin['experimental.chat.system.transform']({}, missing);
  assert.deepEqual(missing.system, []);
  assert.ok(!calls.includes('/wrong-load-directory'));
});

test('V1 Learn/Reset keep main conversation, arguments and attachment identity; unknown commands untouched', async () => {
  const plugin = await makePlugin()({ client: { session: { get: async () => ({ data: { directory: resolve('.') } }) } } });
  for (const name of ['learn', 'reset']) {
    const parts = [{ type: 'text', text: 'Original arguments', id: 'part-existing' }, { type: 'file', url: 'keep' }];
    const output = { parts };
    await plugin['command.execute.before']({ command: `vibe-wise-${name}`, sessionID: 'main' }, output);
    await plugin['command.execute.before']({ command: `vibe-wise-${name}`, sessionID: 'main' }, output);
    assert.equal(output.parts, parts);
    assert.equal(parts[0].id, 'part-existing');
    assert.match(parts[0].text, /main conversation/);
    assert.match(parts[0].text, /Original arguments/);
    assert.equal(parts[0].text.split('The user explicitly invoked').length, 2);
    if (name === 'reset') assert.match(parts[0].text, /not reset confirmation/);
  }
  const unknown = { parts: [{ type: 'text', text: 'User command' }] };
  await plugin['command.execute.before']({ command: 'user-command' }, unknown);
  assert.equal(unknown.parts[0].text, 'User command');
});

function v2Context() {
  const hooks = new Map(), commands = new Map(), sent = [], disposed = [];
  const registration = name => ({ dispose: async () => { disposed.push(name); } });
  return {
    hooks, commands, sent, disposed,
    ctx: {
      location: { directory: '/wrong-load-directory' },
      session: {
        get: async ({ sessionID }) => ({ location: { directory: `/${sessionID}` } }),
        hook: async (name, callback) => { hooks.set(name, callback); return registration(name); },
        prompt: async prompt => { sent.push(prompt); },
      },
      command: { transform: async callback => {
        callback({ add: command => commands.set(command.name, command) }); return registration('commands');
      } },
    },
  };
}

test('V2 registers actual context/compaction hooks, deduplicates per request, restores every continuation and disposes', async () => {
  const { ctx, hooks, disposed } = v2Context();
  const cleanup = await makeSetup(async directory => `Restore ${directory}`)(ctx);
  assert.deepEqual([...hooks.keys()], ['context', 'compaction']);
  for (const name of hooks.keys()) {
    const event = { sessionID: 'session-worktree', system: [{ type: 'text', text: 'Keep user system' }] };
    await hooks.get(name)(event);
    await hooks.get(name)(event);
    assert.equal(event.system.length, 2);
    assert.equal(event.system[1].text, 'Restore /session-worktree');
    const continuation = { sessionID: 'session-worktree', system: [] };
    await hooks.get(name)(continuation);
    assert.equal(continuation.system[0].text, 'Restore /session-worktree');
  }
  await cleanup();
  assert.deepEqual(disposed.sort(), ['commands', 'compaction', 'context']);
});

test('V2 preserves session, prompt attachments and delivery without touching agents/models/permissions', async () => {
  const { ctx, commands, sent } = v2Context();
  await makeSetup(async () => null)(ctx);
  for (const name of ['learn', 'reset']) {
    const attachments = [{ type: 'file', url: 'keep' }];
    await commands.get(`vibe-wise-${name}`).execute({ sessionID: 'main',
      prompt: { text: 'Original args', attachments }, delivery: 'queue' });
    assert.equal(sent.at(-1).sessionID, 'main');
    assert.equal(sent.at(-1).attachments, attachments);
    assert.equal(sent.at(-1).delivery, 'queue');
    assert.match(sent.at(-1).text, /main conversation/);
    assert.match(sent.at(-1).text, /Original args/);
  }
});

test('V2 partial setup failure disposes existing registrations', async () => {
  const { ctx, disposed } = v2Context();
  ctx.command.transform = async () => { throw new Error('Registration failed'); };
  await assert.rejects(makeSetup()(ctx), /Registration failed/);
  assert.deepEqual(disposed.sort(), ['compaction', 'context']);
});

test('Python bridge reads actual active/paused notes and does not modify history', async t => {
  const temporary = await mkdtemp(join(tmpdir(), 'vibe-wise-node-'));
  // Fixture contains only test-owned files. Use native fs cleanup, not shell commands.
  t.after(async () => { const { rm } = await import('node:fs/promises'); await rm(temporary, { recursive: true }); });
  await mkdir(join(temporary, '.git'));
  const state = join(temporary, '.vibe-wise');
  await mkdir(state);
  await writeFile(join(state, 'profile.md'), 'Learning mode: active\nOnboarding: incomplete\n');
  const progress = '## Old history\n' + 'Evidence\n'.repeat(40000) + '## Pending decision\nAwaiting implementation approval\n';
  await writeFile(join(state, 'progress.md'), progress);
  const context = await contextFor(temporary);
  assert.match(context, /Search the entire progress.md/);
  assert.match(context, /Restarting or compacting is not approval/);
  assert.equal(await readFile(join(state, 'progress.md'), 'utf8'), progress);
  await writeFile(join(state, 'profile.md'), 'Learning mode: paused\n');
  assert.equal(await contextFor(temporary), null);
  assert.equal(await contextFor('relative'), null);
});
