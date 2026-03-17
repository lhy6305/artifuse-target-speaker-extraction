# Artifuse Target Speaker Extraction

Public GitHub backup repository for the `TSE-Prefix` project.

This repository is used to track:

- source code and scripts
- configs and project structure
- design notes and phase reports
- lightweight public-safe summaries and recovery metadata

This repository is not used to publish raw datasets or copyright-restricted
assets, local experiment checkpoints, generated audio payloads, or manifests
that point at local/private assets.

## Local-Only Content

The Git setup intentionally keeps the following out of version control:

- raw/source audio
- game-derived voice packages
- text label files tied to local datasets
- manifests that point at local/private asset paths
- generated synthetic audio datasets
- local runtime caches and logs
- experiment checkpoints and tensor/binary payloads
- generated evaluation audio packs

The Git setup intentionally keeps the following versionable for recovery:

- `reports/daily/` long-lived human-readable progress notes
- `experiments/**/train_summary.json`
- `reports/eval/**/eval_summary.json`
- `reports/eval/**/summary.json`
- blind-pack metadata such as `README.md`, `blind_key.json`, and `sample_meta.json`

If a directory contains both heavy local-only outputs and small public-safe
summaries, the summaries should remain trackable instead of being ignored
wholesale.

If a checkpoint exceeds GitHub's normal file-size limits, publish it through
Git LFS or an external model host instead of committing it directly.

## Repo

- Branch: `main`
- Remote: `https://github.com/lhy6305/artifuse-target-speaker-extraction.git`
- License: `MPL-2.0`

This repository is maintained primarily for self-use backup and progress
tracking. Public-facing documentation is intentionally minimal.
