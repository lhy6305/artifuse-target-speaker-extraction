# Arbitrary Pair A/B Pack

Manifest row example:

{"sample_id":"real_0001","mixture_audio_path":"data/references/real_eval/real_0001/mixture.wav","target_audio_path":"data/references/real_eval/real_0001/target.wav","reference_audio_path":"data/references/real_eval/real_0001/reference.wav","note":"optional"}

Each sample directory contains mono mixture/reference, optional mono target.wav, and two mono model outputs.

Listening sheet rubric:

- `better_output`: `file_a` / `file_b` / `tie` / `uncertain`
- `file_*_source_retention`: choose from `excellent, good, fair, weak, lost`
- `file_*_interference_leak`: choose from `none, slight, moderate, heavy, extreme`
- `file_*_volume_fluctuation`: choose from `none, slight, moderate, heavy, extreme`
- `file_*_artifact`: choose from `none, slight, moderate, heavy, extreme`
- `decision_tags`: optional semicolon-separated tags, e.g. `better_source_retention;less_interference_leak`
- all files in one sample folder share the same safety gain, so playback is more stable while relative A/B level differences are preserved
- export audio is always downmixed to mono before scoring, so mixture/reference/target/candidates share the same channel layout
