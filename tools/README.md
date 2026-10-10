# Asset generator

Every visual in `/assets` is generated — never hand-edit the SVGs.

| Script | Produces | Data |
| --- | --- | --- |
| `generate_assets.py` | hero, section headers, terminal, profile card, expertise cards, skill chart, stack labels/chips, buttons, footer | static copy in the script |
| `stats.py` | `stats-*.svg` — KPI row + language share bar | GitHub GraphQL (live) |
| `streak.py` | `streak-*.svg` — energy-core streak: progress ring vs record, 52-week radial ring, growth curve, 90-day track, 26-week bars | GitHub GraphQL (live) |
| `contrib3d.py` | `contrib3d-*.svg` — isometric 3D calendar of the last 52 weeks | GitHub GraphQL (live) |

Shared pieces live in `svgkit.py` (fonts → vector paths, theme tokens, the
frosted-glass card with drifting aurora orbs, isometric prism helpers) and
`ghdata.py` (GraphQL + contribution calendar).

```powershell
pip install fonttools
python tools/generate_assets.py tools/fonts assets
$env:GITHUB_TOKEN = (gh auth token)
python tools/stats.py assets lokeshe09
python tools/streak.py assets lokeshe09
python tools/contrib3d.py assets lokeshe09
```

Text is converted to paths with Inter + JetBrains Mono (`tools/fonts/`, OFL),
so rendering is identical on every OS. Each asset is emitted as `*-dark.svg`
and `*-light.svg`; the README switches between them with `<picture>` +
`prefers-color-scheme`.

`.github/workflows/profile-assets.yml` rebuilds the three live cards daily
(and on every push) and commits them back to `assets/` with `[skip ci]`. If a
live build fails it keeps the committed card, so the README never shows a
broken image.

Edit copy, colours (`THEMES` / `GLASS`), skills (`SKILLS`) or cards (`CARDS`)
in the scripts, re-run, commit.
