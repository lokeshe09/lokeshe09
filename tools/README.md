# Asset generator

All visuals in `/assets` are generated — never hand-edit the SVGs.

```powershell
pip install fonttools
# fonts dir must contain: Inter-{Bold,SemiBold,Medium,Regular}.ttf, JetBrainsMono-{Medium,Bold}.ttf
#   Inter          → https://github.com/rsms/inter/releases
#   JetBrains Mono → https://github.com/JetBrains/JetBrainsMono/releases
python tools/generate_assets.py <fonts-dir> assets
```

Text is converted to vector paths, so rendering is identical on every OS.
Each asset is emitted as `*-dark.svg` and `*-light.svg`; the README switches
between them with `<picture>` + `prefers-color-scheme`.

Edit copy, colors (`THEMES`), skills (`SKILLS`) or cards (`CARDS`) in the
script, re-run, commit.

## Live cards (streak + analytics)

`tools/stats.py` renders the analytics panel (commits, contributions, active days,
repos, PRs, languages + language-share bar). `tools/streak.py` pulls the full contribution calendar from the GitHub GraphQL
API and renders `streak-dark.svg` / `streak-light.svg` — total contributions,
current streak (ring = % of personal record), longest streak, and a 26-week
sparkline. `.github/workflows/profile-assets.yml` runs it daily (and on every
push) and publishes to the `output` branch alongside the snake; the README
reads from there. The copy in `assets/` is only a fallback if the live build fails.

```powershell
$env:GITHUB_TOKEN = (gh auth token); python tools/streak.py assets lokeshe09
```

```powershell
$env:GITHUB_TOKEN = (gh auth token); python tools/stats.py assets lokeshe09
```
