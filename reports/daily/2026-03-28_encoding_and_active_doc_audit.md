# 2026-03-28 encoding and active doc audit

## Summary

- Goal:
  stop experiment push for one turn,
  audit active docs for encoding damage,
  and lock a new doc convention.
- Result:
  no BOM was found in the active docs that were checked.
- Result:
  no on-disk mojibake was found in the active docs that were checked.
- Root cause:
  the visible garbling risk came from PowerShell text decoding behavior,
  not from confirmed UTF-8 corruption on disk.
- Action:
  active docs were rewritten into English-only ASCII.

## Files Audited

- `docs/01_project_overview_and_plan.md`
- `docs/02_pitfalls_log.md`
- `docs/05_task_branch_map.md`
- `reports/daily/index_2026-03.md`
- `reports/daily/2026-03-28_parallel_prepresent_jointcancelhead_v176_followup.md`
- `reports/daily/2026-03-28_parallel_prepresent_broaderpath_targetproj_v177_v180_followup.md`

## Findings

- All checked files were UTF-8 readable.
- No checked file started with a UTF-8 BOM.
- The two active daily reports created in this session were already ASCII-only.
- The old active docs and daily index were not corrupted on disk,
  but they were not compliant with the new English-only ASCII convention.

## New Convention

- Active docs and active daily reports must be English-only and ASCII-only.
- User-facing assistant replies still stay in Simplified Chinese.
- Repo docs must be treated as UTF-8 on disk.
- Do not use default PowerShell text decoding for repo docs.
- Do not use PowerShell text write APIs for repo docs or reports.
- Use `apply_patch` for doc writes so files stay BOM-free.

## Immediate Follow-Up

- Rewrote the active docs into ASCII-only English.
- Rewrote the active March daily index into ASCII-only English.
- Added the encoding pitfall to the active pitfalls log.
- No experiment work was continued in this turn.
