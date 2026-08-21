# The Associated Guess

**SERIOUS NEWS. ABSURD WORLD.**

Static satire newspaper site. Content is generated from the OpenClaw vault at `G:\openclaw\business\satire-news\`.

## Build

```powershell
py -3 scripts/build_from_vault.py
```

After verifying the site locally, archive vault files that are now on the site:

```powershell
py -3 scripts/build_from_vault.py --archive-used
py -3 G:\LocalAIagent\desktop-agent\integrations\satire_vault_monitor.py --rebuild
```

## Preview

```powershell
powershell -File scripts/preview.ps1
```

Open http://localhost:8081/

**Live (GitHub Pages):** https://laughingdragonsproductions.github.io/Theassociatedguess/

## Notes

- Top 4 above-the-fold stories randomize on each homepage load (`assets/js/paper.js`).
- Subscribe CTAs are hidden via CSS until paid subscription launches (`.subscribe-cta`).
- Display dates in `data/articles.json` are synthetic (Jan–Aug 2026) for an established-paper look.
