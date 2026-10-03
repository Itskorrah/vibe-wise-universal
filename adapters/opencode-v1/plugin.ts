import type { Plugin, Hooks } from '@opencode-ai/plugin';
import { contextFor, commandPrompt, addOnce } from '../opencode-common/bridge.mjs';

// Type-only SDK import: OpenCode supplies the runtime; no extra production package.
export const makePlugin = (restore = contextFor): Plugin => async ({ client }) => {
  const forSession = async (sessionID?: string) => {
    if (!sessionID) return null;
    const response = await client.session.get({ path: { id: sessionID } });
    return response.data?.directory ?? null;
  };
  const hooks: Hooks = {
    'experimental.chat.system.transform': async (input, output) => {
      const directory = await forSession(input.sessionID);
      if (directory) addOnce(output.system, await restore(directory));
    },
    'experimental.session.compacting': async (input, output) => {
      const directory = await forSession(input.sessionID);
      if (directory) addOnce(output.context, await restore(directory));
    },
    'command.execute.before': async (input, output) => {
      const names: Record<string, string> = { 'vibe-wise-learn': 'learn', 'vibe-wise-reset': 'reset' };
      const name = names[input.command];
      if (!name) return;
      const directory = await forSession(input.sessionID);
      if (!directory) throw new Error('Cannot locate the VibeWise command session.');
      // Preserve attachments and other command content. No subagent or model override.
      const text = commandPrompt(name, directory);
      const part = output.parts.find(part => part.type === 'text');
      if (!part || part.type !== 'text') throw new Error('VibeWise command has no text prompt.');
      if (!part.text.includes(text)) part.text = `${text}\n\n${part.text}`;
    },
  };
  return hooks;
};

export default makePlugin();
