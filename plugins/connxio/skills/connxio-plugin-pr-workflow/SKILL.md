---
name: connxio-plugin-pr-workflow
description: Governs how changes to this plugin repository (skills, plugin.json, or any other file under plugins/connxio) get committed and turned into pull requests. Use whenever making or finishing a change to a skill, adding a new skill, or otherwise editing this repo.
argument-hint: "skill change or addition being made to this repo"
---

# Connxio Plugin PR Workflow

This skill governs the process for changing anything in this plugin
repository (`connxio/plugins`) — adding a new skill, editing an existing
`SKILL.md`, updating `plugin.json`, or any other file under
`plugins/connxio`.

## Hard rule: always ask before creating a pull request

- **Never open a pull request without first explicitly asking the user and
  getting confirmation** — even if the requested change is complete and
  verified. The user may want to make further changes before a PR is opened.
- It is fine to make the file edits, commit them locally, and even push to a
  branch without asking — asking is specifically required before the
  **PR-creation step** (`gh pr create` or equivalent).
- If a pull request for the branch/change already exists and the user asks
  for an additional, closely related change to the same skill(s), it's fine
  to push more commits to update that existing PR without asking again —
  the "ask first" rule is about *opening new PRs*, not about updating one
  that was already explicitly opened for this change.
- If unsure whether a new PR is warranted or whether to add to an existing
  one, ask the user rather than guessing.

## Hard rule: always bump the plugin version

- Every PR that changes anything under `plugins/connxio` must also bump the
  `version` field in `plugins/connxio/.claude-plugin/plugin.json` (patch
  version bump, e.g. `0.1.4` -> `0.1.5`, unless the user specifies otherwise).
- Check the current version on `main` before bumping (it may have moved
  since your last change if other PRs were merged) — don't assume the
  version you last set is still current.
- Do this in the same commit/PR as the skill change, not as a separate
  follow-up.

## Recommended procedure

1. Make the requested skill/file edit(s).
2. Check `plugin.json`'s current version against `origin/main` and bump it
   (patch bump by default) in the same change set.
3. Create a branch off `origin/main` (not off any other in-progress branch)
   named for the change (e.g. `fix-script-action-datacollection-refs`).
4. Commit and push the branch.
5. **Stop and ask the user for explicit confirmation before running
   `gh pr create`** (or opening a PR any other way). Summarize what the PR
   would contain.
6. Only after the user confirms, create the PR.
7. If the user asks for more changes to the same skill before confirming,
   make them, push additional commits to the same branch, and ask again
   before creating the PR.
