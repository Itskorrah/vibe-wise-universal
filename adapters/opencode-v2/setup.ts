import type { Plugin } from '@opencode/plugin';
import { contextFor, commandPrompt } from '../opencode-common/bridge.mjs';

export const makeSetup = (restore = contextFor): Plugin.Plugin['setup'] => async (ctx) => {
  const registrations: { dispose(): Promise<void> }[] = [];
  const forSession = async (sessionID: Parameters<typeof ctx.session.get>[0]['sessionID']) => {
    const session = await ctx.session.get({ sessionID });
    return session.location.directory;
  };
  // Request-local deduplication. No permanent session cache that can hide compaction.
  const inject = async (event: Parameters<Parameters<typeof ctx.session.hook<'context'>>[1]>[0]) => {
    const directory = await forSession(event.sessionID);
    const text = await restore(directory);
    if (text && !event.system.some(part => part.text === text))
      event.system.push({ type: 'text', text });
  };
  try {
    registrations.push(await ctx.session.hook('context', inject));
    registrations.push(await ctx.session.hook('compaction', inject));
    registrations.push(await ctx.command.transform(editor => {
      for (const name of ['learn', 'reset']) editor.add({
        name: `vibe-wise-${name}`,
        description: `Explicit VibeWise ${name} in the main conversation`,
        execute: async ({ sessionID, prompt, delivery }) => {
          const directory = await forSession(sessionID);
          await ctx.session.prompt({ ...prompt, sessionID, delivery,
            text: `${commandPrompt(name, directory)}\n\n${prompt.text}` });
        },
      });
    }));
  } catch (error) {
    await Promise.all(registrations.map(registration => registration.dispose()));
    throw error;
  }
  // Host-scoped registrations dispose on unload; also expose explicit cleanup.
  return async () => { await Promise.all(registrations.map(registration => registration.dispose())); };
};
