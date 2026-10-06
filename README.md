# Skills

Agent Skills for Claude.

| Skill | Description |
| --- | --- |
| [audio-blackframe-splitter](audio-blackframe-splitter/) | Splits an audio file into fixed-length black-video `.mp4` clips (solid black frame + matching audio segment) for feeding AI lip-sync tools like Seedance as a "video input." |
| [seedance-2-5-skill](seedance-2-5-skill/) | Seedance 2.5 / 2.0 prompt creation engine and generation workflow: route selection, Seedream 5.0 Pro storyboards, reference binding, staged long video, review loop. Executes through the Higgsfield MCP (`seedance_2_5`) or Atlas Cloud. |
| [universal-video-prompt-skill](universal-video-prompt-skill/) | Model-agnostic video prompt spec (scope, locks, time) compiled per model, with measured model profiles and degrade rules. Required companion of `seedance-2-5-skill`. |
| [atlas-cloud](atlas-cloud/) | Atlas Cloud API and MCP integration: 300+ image, video, audio, 3D and LLM models behind one key; model discovery, upload, generate, poll. Default Atlas execution route for `seedance-2-5-skill`. |

## Seedance 2.5 stack

`seedance-2-5-skill` is the prompt engine, `universal-video-prompt-skill` holds
the shared spec format and model-profile schema it links to, and generation
goes through whichever provider is exposed in the conversation:

- **Higgsfield MCP** (primary in Claude):
  [`seedance-2-5-skill/references/execution-higgsfield-mcp.md`](seedance-2-5-skill/references/execution-higgsfield-mcp.md)
  maps every creative route to a `seedance_2_5` mode and media role, carries the
  live parameter surface (4–30 s, 480p–1080p, `t2v` / `omni_reference` /
  `video_edit` / `video_extension`, start and end frame roles), the
  `generate_video` → `jobs_wait` → `show_generation_by_ids` flow, and folds in
  Higgsfield's *Seedance 2.5: Complete Prompting Guide* (GLOBAL STYLE at the
  top, labelled shots closing with `Hard cut.`, AUDIO last; one reference per
  element; settings over prose).
- **Atlas Cloud**: the upstream `atlas-skill` / `atlas-mcp` / `atlas-cli` /
  `atlas-rest` routes in
  [`seedance-2-5-skill/references/execution-adapters.md`](seedance-2-5-skill/references/execution-adapters.md),
  backed by the `atlas-cloud` skill and an `ATLASCLOUD_API_KEY`.

A `higgsfield/seedance_2_5` capability profile (and a short `seedance_2_0`
sibling) lives in
[`seedance-2-5-skill/references/model-profile.md`](seedance-2-5-skill/references/model-profile.md),
read from the Higgsfield catalog on 2026-09-21. Re-run `models_explore` before
quoting it.

### Install elsewhere

From the upstream repositories (no Higgsfield route):

```bash
npx skills add AtlasCloudAI/awesome-seedance-2.5-prompts-skills --skill seedance-2-5-skill
npx skills add AtlasCloudAI/awesome-seedance-2.5-prompts-skills --skill universal-video-prompt-skill
npx skills add AtlasCloudAI/atlas-cloud-skills --skill atlas-cloud
```

From this repository (includes the Higgsfield route): clone it and copy the
three folders into `~/.claude/skills/`, or point the `skills` CLI at it:

```bash
npx skills add arperture/skills --skill seedance-2-5-skill
npx skills add arperture/skills --skill universal-video-prompt-skill
npx skills add arperture/skills --skill atlas-cloud
```

`seedance-2-5-skill` links to `../universal-video-prompt-skill`, so install the
two side by side. Restart Claude Code (or run `/skills`) afterwards.

## Attribution

| Skill | Source | Commit | License |
| --- | --- | --- | --- |
| seedance-2-5-skill | [AtlasCloudAI/atlas-cloud-skills](https://github.com/AtlasCloudAI/atlas-cloud-skills) `skills/seedance-2-5-skill`, a synced copy of [AtlasCloudAI/awesome-seedance-2.5-prompts-skills](https://github.com/AtlasCloudAI/awesome-seedance-2.5-prompts-skills) with a newer CLI credential guard | `d31ff93` (2026-09-21) | CC BY 4.0 (see the folder's `LICENSE`) |
| universal-video-prompt-skill | same | `d31ff93` (2026-09-21) | CC BY 4.0 (see the folder's `LICENSE`) |
| atlas-cloud | [AtlasCloudAI/atlas-cloud-skills](https://github.com/AtlasCloudAI/atlas-cloud-skills) `atlas-cloud` | `d31ff93` (2026-09-21) | not stated upstream at that commit |

Local changes on top of upstream:

- `seedance-2-5-skill`: new `references/execution-higgsfield-mcp.md`; a
  `higgsfield/seedance_2_5` profile in `references/model-profile.md`; the
  Higgsfield route wired into `SKILL.md` (description, route table, execution
  layer) and `references/execution-adapters.md`.
- `universal-video-prompt-skill`: one Higgsfield paragraph in
  `references/execution.md`.
- `atlas-cloud`: unchanged.

The Higgsfield prompt dialect draws on Higgsfield's published
[Seedance 2.5 prompting guide](https://higgsfield.ai/blog/seedance-2-5-prompting-guide)
and on the Dreamina conventions relayed by O-Side Media's MIT-licensed
[higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill).
