## Learned User Preferences

- Replace the default Clips Kitty marketing end card with a personal channel animated MP4 bumper on generated clips.
- Prefer a phased rollout: run and validate from source first; defer public installers until fork safety (updates, branding) is settled.
- Expect MCPs and tooling for exploration, implementation, and code audits—not guesswork.
- Keep upstream improvements via git merge while preserving fork-only features (custom outro, fork update policy).
- Use branding/watermark during the clip plus a custom end card when end-of-clip promotion matters.

## Learned Workspace Facts

- Fork of ColinGPT9/clips-studio; GitHub origin is ilodhi/clips-studio with upstream remote ColinGPT9/clips-studio.
- Custom end card: `clips.custom_outro`, uploads under `data/outro/uploads/`, API `POST /outro/source`, Settings → Branding UI in `video/outro.py`.
- Fork defaults ship `clips.outro: false` in `config/settings.yaml` until a custom bumper is configured or end cards are turned on.
- Packaged fork builds use `config/fork.json` (`updates: false`) and commented-out ColinGPT9 publish URL so electron-updater does not pull upstream binaries.
- Routine upstream sync: `scripts/merge-upstream.ps1` or `git fetch upstream && git merge upstream/main`; common conflict files include `video/outro.py`, `server/api.py`, `Settings.tsx`, `electron-builder.yml`.
- Day-to-day dev: `pip install -r requirements.txt`, then `cd ui && npm install && npm run dev`; fork workflow documented in `FORK.md` (AGPL-3.0).