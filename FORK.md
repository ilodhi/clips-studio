# ilodhi fork — custom channel end card

This repository is a fork of [Clips Kitty](https://github.com/ColinGPT9/clips-studio)
(AGPL-3.0). It adds a **custom MP4 end card** so generated Shorts end with your
bumper instead of the default “Made with Clips Kitty” animation.

Upstream changes are merged from `upstream` (`ColinGPT9/clips-studio`). This fork’s
`main` may include channel-specific defaults and docs only on this branch.

## Run from source (Phase 1)

```bash
git clone https://github.com/ilodhi/clips-studio.git
cd clips-studio
pip install -r requirements.txt

cd ui
npm install
npm run dev
```

The desktop app starts the Python engine automatically. Keep the app open while clipping.

### Set your end card

1. Open **Settings** → scroll to **Branding** (bottom).
2. Click **Choose end card video** and pick your animated **MP4** (9:16 works best).
3. Turn **Append … end card** **on** if it is off (upload may turn it on for you).
4. Queue a video and generate clips. **New** renders get your bumper at the end.

Clips made **before** you set the bumper are unchanged until you re-render them.

### Bumper tips

- **9:16** vertical; important text away from the bottom ~480px (TikTok caption zone).
- Any length is fine; the engine matches each clip’s resolution, frame rate, and audio layout.
- **Watermark / branding** (Generate bar or editor) is separate — use both for handle + bumper.

### Defaults in this fork

- `clips.outro` defaults to **false** in `config/settings.yaml` so batches do not get the
  Kitty card until you opt in or upload a custom bumper.

### Staying current with upstream

**Regularly** (monthly or before a big clip batch):

```bash
git fetch upstream
git merge upstream/main
```

On Windows you can run:

```powershell
.\scripts\merge-upstream.ps1
```

Conflicts often touch `video/outro.py`, `ui/src/renderer/src/pages/Settings.tsx`,
`server/api.py`, and `ui/electron-builder.yml`. Keep fork-only commits small.

After merging upstream, run from source and clip a short test video before you rely on it.

### In the app (source checkout only)

**Settings → Fork updates**

| Button | What it does |
|--------|----------------|
| **Check upstream for conflicts** | Fetches ColinGPT9 and lists files both you and upstream changed (especially fork-only files). |
| **Pull updates from my repo** | `git pull` from `origin` — use after you pushed from another PC or merged on GitHub. |
| **Merge upstream into this copy** | Enabled only when the check says it is safe (no overlap in fork-critical files). |

You do **not** need to uninstall. Pull or merge in git, restart `npm run dev`, and continue.

Packaged `.exe` installs do not include a git clone; use a **source checkout** for this UI, or your own installer feed later.

## Phase 2 — updates and installer safety

This fork **does not** check ColinGPT9’s Hugging Face update feed. That prevents a
packaged install from silently replacing your custom engine with upstream Clips Kitty.

| File | Purpose |
|------|---------|
| `config/fork.json` | `updates: false` — read at runtime from `resources/fork.json` |
| `ui/electron-builder.yml` | `publish` block commented out; `fork.json` bundled in `extraResources` |
| Settings → Updates | Shows fork message instead of “Check for updates” |

### When you ship your own installer later

1. Create a Hugging Face repo for release payloads (see upstream `docs/RELEASING.md`).
2. Set `config/fork.json` to `"updates": true` and add your feed URL as `releaseFeed`.
3. Uncomment `publish` in `ui/electron-builder.yml` and point `url` at **your** HF repo.
4. Rebuild with `python scripts/build_installer.py` (CUDA torch, long build).

Until then, install from **source** (`npm run dev`) or distribute a zip you built yourself,
and update by `git pull` + rebuild.

### Do not install upstream’s Web Setup on top of this fork

The official Clips Kitty installer expects ColinGPT9’s update channel. Use **this repo’s**
build or source only.

## Licence

Clips Kitty is AGPL-3.0-or-later. Modifications in this fork are under the same
licence when you distribute the software. Your videos and clips remain yours.