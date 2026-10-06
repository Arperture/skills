# Model profiles: Seedance family

Measured behaviour, not documented behaviour. The compiler reads these fields to
decide what to emit and what to degrade.

Field definitions and the blank template live in
[the Universal Video Prompt Skill](../../universal-video-prompt-skill/references/model-profile-schema.md).
If that link does not resolve, the Seedance 2.5 Skill installation is incomplete.
Help the user install `universal-video-prompt-skill` before continuing and **do not
invent a schema**.

**Unknown is a valid value.** An empty field prompts a probe; a guessed field
silently corrupts every run built on it.

---

## `bytedance/seedance-2.0`

Last verified: 2026-08-03

### Capability layer

| Field | Value | How verified |
|---|---|---|
| Reference addressing | `@image1`, `@image2`, … | Generation |
| Max references | 9 images | Provider docs |
| Multi-shot in one generation | yes — ordered segments with cuts | 15s multi-segment run |
| Hard cut support | yes | Same |
| Duration range | 4–15s | Provider docs |
| Resolution | 480p, 720p, 1080p depending on provider | Provider model page |
| Native audio | yes | Generation with audio enabled |
| Timing adherence | Requested beats land **~2s late** across a 15s piece; segment **order holds** | Controlled 15s run against a timestamped prompt |
| Recommended granularity | **stages** | Derived from the row above |
| Extension / chaining | via tail-frame chaining | — |
| Audio-only reference | not supported | Provider docs |

### Bias layer

| Field | Value | How verified |
|---|---|---|
| Default aesthetic bias | Strong cinematic priors; interprets sparse prompts well and improvises sensibly | A/B against an over-specified variant of the same segment |
| Effective anti-default phrasing | **Name the drawing tool, not the abstract property.** `crayon / coloured pencil / coarse brush, visible stroke direction, uneven fill, ragged edges` produced genuinely hand-drawn marks | Controlled A/B on one hand-drawn VFX spec |
| Ineffective or overshooting | **`graphically flat, never photoreal` — satisfied exactly and uselessly.** The model honoured it with smooth neon-tube vector outlines and even fill: flat, but not hand-drawn at all. Swapping this one lock for tool names reversed the result on the same spec | Same A/B as above |
| Ineffective or overshooting | **Storyboard-grid over-specification scores worse than text-only staging** on heavy-VFX segments — it suppresses the camera priors that make those shots work | A/B on the same segment |
| Negative-lock behaviour | Respected. Front-load them | Iteration |
| Reference-versus-text priority | **The image wins.** Composition references override written composition | Iteration |
| Handheld / POV | Executes handheld POV convincingly, including motion blur on fast follows and a hand entering frame from below | Hand-drawn VFX spec, v2 |
| Live-action texture retention | Strong. Keeps real bone, glass, stone, and ceiling fixtures at their own colour while a drawn layer sits on top | Same |
| **Prompt-length tolerance** | **High.** A longer revision kept the hand, the opening transformation, the drawn texture, and gained the new beats. A comparison model on the same two prompts lost all three | v3 of the same spec |
| Contact shadows unprompted | Adds a cast shadow under a drawn object sitting on a real surface, without being asked. This is the strongest available evidence of the "both media share one physical space" contract | v3 |
| Spatial containment | Reads `open plinth` correctly — renders plinth surface, support rod, and shadow, not a vitrine | v3 |

### Known failure modes

| Symptom | Detail | Handling |
|---|---|---|
| Small text errors | UI labels and signage render with character-level errors and garbled small type | Post-production for anything that must read exactly |
| Dropped list items | Enumerated menu entries partially render — some items simply absent | Reduce the count, or add the text in post |
| Camera move ignored | A stated move is skipped while the rest of the segment lands correctly | Re-state the move as the segment's primary intent, or accept and reframe |
| Timeline drift | Whole timeline shifts later, ~2s over 15s | Use stages; if second-level is required, write beats early and verify |
| **Dropped stages under load** | A 15s piece with **four** staged events rendered only stages 1 and 4 — the two middle stages were skipped entirely, not merely delayed. Raising event density per stage while keeping five shorter stages did **not** reproduce the drop | Treat ~4 distinct state-changes in 15s as the ceiling. If the spec needs more, either shorten each stage and raise density, or split across requests |

### Compile notes

- Emit `@imageN`. Never bracketed or spelled-out reference labels.
- Default to `stages`.
- Prefer text-driven staging over feeding a storyboard grid for heavy-VFX and
  large-scale segments.
- When a composition reference and written composition conflict, drop the written
  one — it will lose anyway and only adds noise.

---

## `bytedance/seedance-2.5`

Last verified: — · Status: **not yet measured**

Availability differs by provider. Verify against the provider's model page before
offering 2.5-specific routes; see [capabilities](capabilities.md).

### Capability layer

| Field | Value | How verified |
|---|---|---|
| Reference addressing | `@Image 1` / `@image1` — **unverified**, confirm against the provider | — |
| Max references | up to 30 images, 10 video, 10 audio, ~50 combined | Launch material |
| Multi-shot in one generation | expected yes | Not measured |
| Duration range | 4–30s | Launch material |
| Resolution | read the provider's model page | — |
| Native audio | yes | Launch material |
| Audio-only reference | supported | Launch material |
| Timing adherence | **not measured** — the single most valuable probe | — |
| Recommended granularity | **unknown** — do not assume it differs from 2.0 | — |
| Editing / extension / bridging | announced; API exposure varies | — |

### Bias layer

Not measured. Do **not** copy 2.0's bias-layer entries here — anti-default
phrasing is per-model by definition, and launch material specifically claims
changed default behaviour around unrequested subtitles and music, which is exactly
the kind of thing a 2.0-tuned negative list would now be redundantly fighting.

### First probes to run, in order

1. **Reference addressing** — one generation with two bound references. Everything
   else is blocked on getting this right.
2. **Timing adherence** — the same spec at `stages` and at `second-level`; measure
   the drift. Fills timing adherence, recommended granularity, and usually a
   failure mode in one run.
3. **Unrequested subtitles and music** — generate with no negatives at all. If
   they no longer appear, 2.0's negative lines are dead weight here.
4. **Reference ceiling in practice** — where stability actually degrades, not where
   the documented limit sits.

Record results here as they land, including negative results.

---

## `higgsfield/seedance_2_5`

Last verified: 2026-09-21 · Provider: Higgsfield MCP (`models_explore`, `action: get`)

The same model family as `bytedance/seedance-2.5` above; this entry records what
the Higgsfield catalog actually exposes. Re-run `models_explore` before quoting
it.

### Capability layer

| Field | Value | How verified |
|---|---|---|
| Model ID | `seedance_2_5` | Catalog |
| Modes | `t2v`, `omni_reference`, `video_edit`, `video_extension` | Catalog |
| Reference addressing | `@Image 1` or `Image 1` in prose, bound by upload order; **unverified by generation** | Higgsfield prompting guide |
| Media roles | `start_image`, `end_image`, `image_references`, `video_references`, `audio_references` | Catalog |
| Max references | up to 30 images / 10 video / 10 audio, about 50 combined | Higgsfield product page; not probed |
| Multi-shot in one generation | expected yes; the guide recommends labelled `Shot N … Hard cut.` | Not measured |
| Hard cut support | expected yes | Not measured |
| Duration range | 4–30 s, default 5; locked to the source in `video_edit` | Catalog |
| Resolution | `480p`, `720p`, `1080p` (default `720p`); 4K only through the separate upscale tool | Catalog |
| Aspect ratio | `auto`, `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`; ignored in `video_edit`, inherits the source in `video_extension` | Catalog |
| Native audio | native (`generate_audio`, default true); audio references accepted | Catalog |
| Audio-only reference | the role exists; whether an audio-only material set is accepted is **unverified** | — |
| First frame / first-and-last frame | supported through `start_image` / `end_image`; ratio follows the first image | Catalog + [capabilities](capabilities.md) |
| Extension or chaining | `video_extension` with `extension_mode` `forward` or `backward`; ratio follows the source | Catalog |
| Video editing | `video_edit`; billed by source duration; duration and ratio locked | Catalog |
| Bitrate | `bitrate_mode` `standard` / `high` | Catalog |
| Genre parameter | none; `seedance_2_0` has `genre` | Catalog |
| Unlimited allowance | not offered for 2.5 on the tested account; `seedance_2_0` reports `supports_unlim` | Catalog |
| Timing adherence | **not measured** | — |
| Recommended granularity | **unknown**; the guide's labelled-shot format is stages by another name | — |

### Bias layer

Not measured. Guide-reported and not yet reproduced here: genre and lighting
choices move pacing, contrast, and camera behaviour more than prompt text does;
conflicting camera grammars in one shot fail; vague transitions between shots
are the leading cause of a sequence breaking. Record A/B results here as they
land.

### First probes to run, in order

1. **Reference addressing**: two bound `image_references`, `@Image 1` versus
   `Image 1`, one generation at 480p.
2. **Timing adherence**: one 20 s spec at stages and at second-level.
3. **Unrequested music and captions**: generate with no negatives at all.
4. **Start and end frame**: matched ratios, then deliberately mismatched, to
   confirm the stretch behaviour.
5. **`video_extension` boundary quality** at 5 s and 15 s extensions.

Catalog drift already observed: an August 2026 community snapshot recorded 720p
max and no start/end-frame roles; the September catalog exposes 1080p and both
roles. Trust the live call.

### Sibling: `higgsfield/seedance_2_0`

| Field | Value | How verified |
|---|---|---|
| Duration range | 4–15 s, default 5 | Catalog, 2026-09-21 |
| Resolution | `480p`, `720p`, `1080p`, `4k` (default `720p`) | Catalog |
| Extra parameters | `mode: std`, `bitrate_mode`, `genre` (`auto / action / horror / comedy / noir / drama / epic`), `generate_audio` | Catalog |
| Media roles | same five roles as 2.5 | Catalog |
| Unlimited allowance | `supports_unlim: true` | Catalog |

Use it for 4K deliverables, a genre hint, or unlimited-allowance drafts under
15 s. Bias-layer findings for `bytedance/seedance-2.0` above were measured on
Atlas Cloud; treat them as hypotheses on Higgsfield until re-checked.

---

## Related

- [model profile schema](../../universal-video-prompt-skill/references/model-profile-schema.md) — field definitions
- [capabilities](capabilities.md) — documented limits and platform-versus-API
- [troubleshooting](troubleshooting.md) — symptom-driven fixes
- [Higgsfield MCP](execution-higgsfield-mcp.md) — submission flow and prompt dialect for the `higgsfield/*` profiles
