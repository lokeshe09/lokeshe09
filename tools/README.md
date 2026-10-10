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
