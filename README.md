# Testerius Brand Repository (sample)

This repository demonstrates how to host a country brand dictionary for the Testerius app.

## Contents

- `index.json` — manifest with file paths and SHA-256 integrity hashes
- `brands/LV/brands_LV.json` — Latvia (LV) brands dictionary (schema=1)
- `tools/validate_repo.py` — validation utility

## Quick start (upload to GitHub)

1) Create an empty GitHub repository (public is easiest if the app downloads without tokens).

2) Push this folder:

```bash
cd testerius-brands-repo-sample
python3 tools/validate_repo.py

git init
git add .
git commit -m "Add LV brand dictionary (schema 1)"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Raw URLs

After pushing, the app can download:

- `index.json`:
  `https://raw.githubusercontent.com/<USER>/<REPO>/main/index.json`

- LV file:
  `https://raw.githubusercontent.com/<USER>/<REPO>/main/brands/LV/brands_LV.json`

## Integrity

LV SHA-256: `77428ffbc7c6a493dfead93584d85cb3c54e2a0c77ee5fdfa7f1465f84b14f13`

## Android integration (outline)

- Download `index.json`
- If `updatedAt` changed or local SHA mismatch, download country file(s)
- Cache JSON in app storage (`filesDir/...`)
- Parse with kotlinx.serialization or Moshi
- Build lookup maps: brandKey → item, alias → brandKey

