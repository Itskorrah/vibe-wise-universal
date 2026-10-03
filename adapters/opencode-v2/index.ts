import type { Plugin } from '@opencode/plugin';
import { makeSetup } from './setup.ts';
// The published Plugin.define is an identity function. Use its typed descriptor
// shape directly so the adapter does not install a second runtime SDK in the host.
export default { id: 'vibe-wise', setup: makeSetup() } satisfies Plugin.Plugin;
