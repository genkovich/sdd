/**
 * Path scoping + project-root discovery for the SDD dashboard server.
 *
 * The host-specific MCP launchers run the package from `<plugin>/server`, so
 * `process.cwd()` is the PLUGIN dir, never the project. Every read/write must be
 * proven to live under `<PROJECT>/docs/` before it touches disk — the inverse of
 * the Telegram channel's `assertSendable` (it refuses to LEAK its own state; we
 * refuse to TOUCH anything outside the project's docs tree).
 */

import { realpathSync, existsSync, statSync } from 'fs'
import { join, resolve, sep, dirname, basename, normalize, isAbsolute } from 'path'

// The plugin's own root — `--cwd <plugin>/server`, so the plugin dir is one up.
// We hard-refuse to ever resolve THIS as the project (the critical trap: reading
// the plugin's own docs/ instead of the user's).
const PLUGIN_ROOT = resolve(import.meta.dir, '..')

/** Files we will read/serve as artifacts. `.size` is matched by basename, not extname. */
export const ALLOWED_EXT = new Set(['.md', '.yaml', '.yml', '.json'])
const ALLOWED_BASENAMES = new Set(['.size'])

let PROJECT_DIR: string | null = null

function hasProjectMarkers(dir: string): boolean {
  return existsSync(join(dir, 'docs')) || existsSync(join(dir, '.git'))
}

function isPluginRoot(dir: string): boolean {
  try {
    return realpathSync(dir) === realpathSync(PLUGIN_ROOT)
  } catch {
    return resolve(dir) === PLUGIN_ROOT
  }
}

/** Walk up from `start` looking for a dir that has `docs/` or `.git` and is not the plugin. */
function walkUp(start: string): string | null {
  let dir = resolve(start)
  for (let i = 0; i < 40; i++) {
    if (!isPluginRoot(dir) && hasProjectMarkers(dir)) return dir
    const parent = dirname(dir)
    if (parent === dir) break
    dir = parent
  }
  return null
}

/**
 * Resolution order (the plan's contract):
 *   1. process.env.CLAUDE_PROJECT_DIR  (Claude Code sets this for the session)
 *   2. an explicit handover from /sdd:start (setProjectDir — authoritative, wins)
 *   3. upward walk from cwd for docs/ or .git
 *   4. null → callers hard-refuse with a clear message
 *
 * (2) is applied by setProjectDir() overriding whatever boot resolved. This
 * function computes the BOOT default — env first, then walk.
 */
function resolveBootDir(): string | null {
  const env = process.env.CLAUDE_PROJECT_DIR
  if (env && existsSync(env) && !isPluginRoot(env) && hasProjectMarkers(env)) {
    return resolve(env)
  }
  return walkUp(process.cwd())
}

PROJECT_DIR = resolveBootDir()

/** The authoritative handover from /sdd:start (runs in-session where cwd IS the project). */
export function setProjectDir(dir: string): string {
  const abs = resolve(dir)
  if (!existsSync(abs)) throw new Error(`project dir does not exist: ${abs}`)
  if (isPluginRoot(abs)) {
    throw new Error(`refusing to use the SDD plugin's own dir as the project: ${abs}`)
  }
  if (!hasProjectMarkers(abs)) {
    throw new Error(`not a project root (no docs/ or .git/): ${abs}`)
  }
  PROJECT_DIR = abs
  return abs
}

export function getProjectDir(): string | null {
  return PROJECT_DIR
}

/** Throw a uniform "where's the project" error for endpoints that need it. */
export function requireProjectDir(): string {
  if (!PROJECT_DIR) {
    throw new Error(
      'project dir unresolved — run /sdd:start in the project (or set CLAUDE_PROJECT_DIR)',
    )
  }
  return PROJECT_DIR
}

export function docsDir(): string {
  return join(requireProjectDir(), 'docs')
}

export function featuresDir(): string {
  return join(docsDir(), 'features')
}

const SLUG_RE = /^[a-z0-9][a-z0-9-]*$/

export function isValidSlug(slug: string): boolean {
  return SLUG_RE.test(slug)
}

/**
 * Resolve `<docs>/features/<slug>/<relPath>` (or a docs-root file when slug is
 * null, e.g. roadmap.md), then PROVE the realpath is contained in docs/, carries
 * an allowed extension, and is not under .git. Returns the absolute path to use.
 *
 * Containment is checked on the realpath so a symlink escaping docs/ is caught.
 * The API is read-only, so the artifact must already exist — a missing file is
 * `no such artifact`, never a write anchor.
 */
export function assertArtifactPath(slug: string | null, relPath: string): string {
  const docs = docsDir()

  // Reject absolute paths and traversal up front (defence in depth — realpath is
  // the real gate, but a clear early refusal beats a confusing one later).
  if (isAbsolute(relPath)) throw new Error(`artifact path must be relative: ${relPath}`)
  const clean = normalize(relPath)
  if (clean.startsWith('..') || clean.split(sep).includes('..')) {
    throw new Error(`path traversal rejected: ${relPath}`)
  }

  if (slug !== null && !isValidSlug(slug)) {
    throw new Error(`invalid slug: ${slug}`)
  }

  const base = slug === null ? docs : join(featuresDir(), slug)
  const target = resolve(base, clean)

  // Extension / basename allowlist.
  const name = basename(target)
  const dot = name.lastIndexOf('.')
  const ext = dot > 0 ? name.slice(dot) : ''
  if (!ALLOWED_BASENAMES.has(name) && !ALLOWED_EXT.has(ext.toLowerCase())) {
    throw new Error(`extension not allowed: ${name}`)
  }

  // Realpath containment. For a missing leaf, anchor on the (existing) parent.
  let realDocs: string
  try {
    realDocs = realpathSync(docs)
  } catch {
    throw new Error(`docs/ does not exist under the project: ${docs}`)
  }
  if (!existsSync(target)) {
    throw new Error(`no such artifact: ${relPath}`)
  }
  const realTarget = realpathSync(target)

  if (realTarget !== realDocs && !realTarget.startsWith(realDocs + sep)) {
    throw new Error(`path escapes docs/: ${relPath}`)
  }
  // Never anything under a .git dir (defence in depth — .git lives outside docs/
  // anyway, but a symlinked .git inside docs/ would be caught here).
  if (realTarget.split(sep).includes('.git')) {
    throw new Error(`refusing to touch .git: ${relPath}`)
  }
  return realTarget
}

/** Content-Type for an artifact path (used by the raw-file endpoint). */
export function contentTypeFor(path: string): string {
  const name = basename(path).toLowerCase()
  if (name === '.size') return 'text/plain; charset=utf-8'
  if (name.endsWith('.md')) return 'text/markdown; charset=utf-8'
  if (name.endsWith('.yaml') || name.endsWith('.yml')) return 'application/yaml; charset=utf-8'
  if (name.endsWith('.json')) return 'application/json; charset=utf-8'
  return 'text/plain; charset=utf-8'
}

/** True if `p` resolves inside the static dashboard dir (used by static-serve). */
export function safeStaticPath(staticRoot: string, urlPath: string): string | null {
  const clean = normalize(urlPath).replace(/^(\.\.(\/|\\|$))+/, '')
  const target = resolve(staticRoot, '.' + sep + clean)
  if (target !== staticRoot && !target.startsWith(staticRoot + sep)) return null
  if (!existsSync(target)) return null
  try {
    if (statSync(target).isDirectory()) return null
  } catch {
    return null
  }
  return target
}
