import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

export const bundle = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const run = promisify(execFile);
export async function contextFor(directory) {
  if (typeof directory !== 'string' || !path.isAbsolute(directory)) return null;
  let python;
  try {
    python = JSON.parse(await readFile(path.join(bundle, 'python.json'), 'utf8')).executable;
  } catch {
    python = process.platform === 'win32' ? 'python' : 'python3';
  }
  try {
    const { stdout } = await run(python, [path.join(bundle, 'scripts/context.py'), '--cwd', directory],
      { timeout: 5000, maxBuffer: 65536, windowsHide: true });
    const result = JSON.parse(stdout);
    return typeof result.context === 'string' ? result.context : null;
  } catch (error) {
    console.error('VibeWise restoration unavailable:', error.message);
    try {
      const result = JSON.parse(error.stdout);
      if (typeof result.error === 'string') return `VibeWise restoration failed: ${result.error}. ` +
        'Explain the problem before continuing active learning. Do not invent approval or notes; ' +
        'repair resources and explicitly resume Learn. This does not activate learning.';
    } catch { /* Interpreter/transport failures have no reliable project state. */ }
    return null;
  }
}

export function commandPrompt(name, directory) {
  if (typeof directory !== 'string' || !path.isAbsolute(directory))
    throw new Error('VibeWise requires the current session project directory.');
  return `The user explicitly invoked VibeWise ${name} for ${JSON.stringify(directory)}. ` +
    `Read ${JSON.stringify(path.join(bundle, 'skills', name, 'SKILL.md'))} and follow it ` +
    'in this main conversation. Resolve all resources from that guide. ' +
    (name === 'reset' ? 'Invocation is not reset confirmation. Preview, ask Cancel / Reset learning, and wait.' :
      'Resume notes without repeating completed onboarding. Never infer implementation approval.');
}

export function addOnce(strings, context) {
  if (context && !strings.includes(context)) strings.push(context);
}
