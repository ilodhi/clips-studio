/** Fork-specific flags shipped beside the packaged app (config/fork.json). */
import { existsSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { app } from 'electron'

export interface ForkConfig {
  /** When false, electron-updater never calls the ColinGPT9 Hugging Face feed. */
  updates?: boolean
  label?: string
  releaseFeed?: string | null
  upstream?: string
}

export function loadForkConfig(): ForkConfig | null {
  const roots = [process.resourcesPath, join(process.resourcesPath, '..')].filter(Boolean)
  for (const root of roots) {
    const path = join(root, 'fork.json')
    if (!existsSync(path)) continue
    try {
      return JSON.parse(readFileSync(path, 'utf8')) as ForkConfig
    } catch {
      return null
    }
  }
  return null
}

export function forkUpdatesDisabled(): boolean {
  if (!app.isPackaged) return false
  const cfg = loadForkConfig()
  return cfg?.updates === false
}