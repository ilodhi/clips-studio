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

```bash
git fetch upstream
git merge upstream/main
```

Conflicts often touch `video/outro.py`, `ui/src/renderer/src/pages/Settings.tsx`, and
`server/api.py`. Keep custom-outro commits small to make merges easier.

## Licence

Clips Kitty is AGPL-3.0-or-later. Modifications in this fork are under the same
licence when you distribute the software. Your videos and clips remain yours.