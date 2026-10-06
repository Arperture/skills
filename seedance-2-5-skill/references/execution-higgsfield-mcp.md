# Higgsfield MCP execution route

Use this route when the Higgsfield MCP tools (`generate_video`,
`generate_video_batch`, `models_explore`, `jobs_wait`, `media_import_url`,
`media_upload`, `show_generation_by_ids`) are exposed in the conversation, or
when the user selects Higgsfield. The Atlas routes in
[execution adapters](execution-adapters.md) stay available when the user selects
them. A user-selected provider always wins.

Creative planning does not change: choose the route in `SKILL.md` §1, enable only
the preparation modules the job needs, and write the prompt with the
scope / locks / time structure. This file covers two things only: how to submit
through Higgsfield, and the prompt dialect Higgsfield's own Seedance 2.5 guide
recommends.

Report `Execution: higgsfield-mcp` only when a Higgsfield tool actually
submitted the job.

## Live catalog: `seedance_2_5`

Snapshot of `models_explore` (`action: get`, `model_id: seedance_2_5`) taken
2026-09-21. Re-run that call before quoting any value below; the catalog moves.
An August 2026 community snapshot recorded 2.5 on Higgsfield as 720p-only with
no start/end-frame roles. Both are exposed now. Never write to an old snapshot.

| Parameter | Values | Notes |
|---|---|---|
| `mode` | `t2v` · `omni_reference` · `video_edit` · `video_extension` | default `t2v` |
| `duration` | 4–30 s, integer | default 5; **ignored** in `video_edit`, which bills by the source video's length |
| `resolution` | `480p` · `720p` · `1080p` | default `720p`; 4K is an upscale step (`upscale_video`), not a parameter |
| `generate_audio` | bool | default `true` |
| `bitrate_mode` | `standard` · `high` | default `standard` |
| `extension_mode` | `backward` · `forward` | **required** for `video_extension`, not allowed otherwise |
| `aspect_ratio` | `auto` · `21:9` · `16:9` · `4:3` · `1:1` · `3:4` · `9:16` | ignored in `video_edit`; follows the source in `video_extension` |
| media roles | `start_image` · `end_image` · `image_references` · `video_references` · `audio_references` | `medias[].value` is a `media_id` or a prior `job_id`, never a URL |

Sibling models in the same catalog:

| Model | Use it when |
|---|---|
| `seedance_2_0` | 4K output (`resolution: 4k`), the `genre` hint (`auto / action / horror / comedy / noir / drama / epic`), or a clip of at most 15 s that the account's unlimited allowance covers (`supports_unlim`) |
| `seedance1_5` | fixed 4 / 8 / 12 s, start and end frame only; cheap drafts |
| `ad_multiplier` | Seedance 2.5 under the hood; reserve it for explicitly requested independent ad variants, per Higgsfield's `ad-multiplier` workflow |

## Route mapping

| Skill route (`SKILL.md` §1) | `mode` | Media roles | Notes |
|---|---|---|---|
| T2V | `t2v` | none | |
| R2V storyboard | `omni_reference` | one `image_references` (the whole board) | The prompt calls it `Image 1` |
| R2V asset references | `omni_reference` | `image_references`, optional `video_references` and `audio_references` | One reference per element that must stay consistent |
| I2V shot pair | `omni_reference` | `start_image`, optional `end_image` | Both images in the same aspect ratio; the output ratio follows the first. State the roles in the prompt as well |
| Extend / chain | `video_extension`, `extension_mode: forward` | `video_references` = the prior clip's `job_id` | Native continuation; ratio inherits the source. Fallback: extract the tail frame, upload it, run I2V with `start_image` |
| Staged whole-short | `t2v` or `omni_reference` | as needed | `duration` up to 30; stages and end states in the prompt |
| Editing | `video_edit` | `video_references` = source, `image_references` = targets | `duration` and `aspect_ratio` ignored; billed by source length |
| Seamless transition | `omni_reference` | two `video_references` | Not a dedicated mode; verify on a 480p pass before a paid final |
| Blockout reference | `omni_reference` | `video_references` = blockout, `image_references` = look | |

## Submission flow

1. **Verify the model** with `models_explore` (`get`, `seedance_2_5`) once per
   session. Read `parameters`, `medias[].roles`, and `aspect_ratios` from the
   response, not from this file.
2. **Bring media in.**
   - HTTPS URL: `media_import_url` (`type: auto`) returns a `media_id`.
   - A file the agent holds: `media_upload` returns a presigned URL; PUT the
     bytes, then `media_confirm`.
   - A file on the user's machine in a Claude Apps UI client: `media_upload_widget`
     as the only tool call in that turn. Never ask for a chat attachment.
   - Output of an earlier generation: pass its `job_id` as `medias[].value`.
3. **Preflight cost** with `generate_video` and `get_cost: true`. State the
   credits before any 1080p or 30 s run. If the response carries `unlim_choice`,
   put that question to the user and call again with `use_unlim` set; never
   decide it for them.
4. **Submit.** One user-facing clip: `generate_video` (`count` 2–4 only for
   variants of the same prompt, inputs, and settings). Two to twelve independent
   shots: `generate_video_batch`, with the shot number as `index`.
5. **Wait.** `jobs_wait` in groups of at most 12, `timeout_seconds` up to 15.
   When `all_terminal` is false, wait `poll_after_seconds` and call again with
   the same job IDs. Then one `show_generation_by_ids` for the whole set.
6. **Review** in the skill's order (identity, locks, end states, motion and
   seams, audio) and regenerate only the failed shot.

Chains run in order: the next segment needs the real prior `job_id`. Cut-based
clips run as one batch.

### Billable-task rules on this route

The state machine in `SKILL.md` applies unchanged. The Higgsfield mapping:

- The **`job_id`** is the prediction ID. Record it with its stage key the moment
  a submission returns.
- `jobs_wait` reports terminal states; anything else is active. Keep polling
  the same ID. Never submit a replacement because a turn ended.
- **A transport timeout on `generate_video` leaves the outcome unknown.** Do not
  resubmit. Check the returned ID, or the account's recent generations, and
  retry only once the original outcome is known.
- A partial `generate_video_batch` failure is not permission to retry the whole
  batch. Keep the returned IDs and resolve the unknown items one by one.
- `get_cost: true` never creates a job. A rejected submission never creates a
  job either, so testing a parameter value is free: a documented enumeration is
  a hypothesis and a submission is the authority.
- `use_unlim: true` only when the user explicitly asks to spend their unlimited
  allowance; the catalog says which models accept it (`supports_unlim`).

## Prompt dialect for Higgsfield

Source: Higgsfield, *Seedance 2.5: Complete Prompting Guide (Full Prompt
Library)*, and *Seedance 2.5 on Higgsfield in 2026*. The rules below are that
guide's. The skill's scope / locks / time structure still governs the content;
where both say the same thing, this file is the shorter statement.

### Shape

One visual rule at the top, one sound rule at the bottom, shots in between.
For anything with more than one camera angle, the shot-by-shot breakdown
outperforms a single continuous scene description.

```text
GLOBAL STYLE: <era, medium, palette, grade, in one line>
SCENE: <one-sentence premise: who, where, what changes>
CHARACTERS: <name, 3–5 visible invariants; reference binding if any>
LOCATION: <space, time of day, weather, what sits in the background>
FIRST FRAME AND BLOCKING: <opening composition; where each subject stands>

Shot 1 — <shot size, angle>. <one observable action>. <camera move, if any>.
End: <visible end state>. Hard cut.
Shot 2 — <shot size, angle>. <action>. End: <state>. Hard cut.
Shot 3 — <shot size, angle>. <action>. End: <final state>.

OPTICS: <lens, depth of field, focus subject>
CAMERA: <the one principle that holds across shots>
PHYSICS: <how fabric, smoke, hair, liquid, weight, and impact behave>
LIGHTING: <where the key is motivated from, its direction, how it falls on faces>
AUDIO: <ambience, specific sound effects, what must not be there>
```

- **Label every shot** with its own action, camera position, and end point, and
  close each with `Hard cut.` Vague transitions are the most common cause of a
  sequence falling apart, so specify camera distance and framing per shot.
- **GLOBAL STYLE and AUDIO are the bookends.** The guide's default audio line is
  `No music, no discernible dialogue` unless the scene needs them. Write
  suppression as a spec (`NO BGM`), not as a preference.
- **PHYSICS** exists because fabric, smoke, hair, and liquid are what look wrong
  when they move like solids.
- **LIGHTING** goes further than GLOBAL STYLE: motivation, direction, fall-off.

Mapped onto the skill's scopes: GLOBAL STYLE, SCENE, OPTICS, CAMERA, PHYSICS,
and LIGHTING are **Global**; CHARACTERS, reference bindings, and AUDIO are
**Locks**; the shot list is **Time**. Restate the two or three most expensive
locks at the physical end, after AUDIO.

### Settings do more than prose

The guide's central finding: genre and lighting settings do more work than most
of the prompt text. Changing genre alone shifts pacing, contrast, and camera
behaviour with an identical scene description. In the Higgsfield web app, era,
genre, lighting angle, physics, lens, emotional tone, and montage pacing are
**selectors** set before the prompt, not described inside it.

Over MCP the picture splits:

| Selector | `seedance_2_5` via MCP | `seedance_2_0` via MCP |
|---|---|---|
| Genre | no parameter; carry it in GLOBAL STYLE and in the shot pacing | `genre` parameter |
| Era, lighting, physics, lens, tone, pacing | prompt text (GLOBAL STYLE, LIGHTING, PHYSICS, OPTICS) | prompt text |
| Resolution, duration, aspect ratio | parameters, never prose | parameters |

Do not write resolution, duration, or aspect ratio into the prompt. They are
parameters, and in `video_edit` and `video_extension` they are locked anyway.

### References

- **One reference per element** that must stay consistent (a face, a product, a
  location, a style) rather than filling the ceiling. A smaller, deliberate set
  beats a cluttered one. Ceilings: 30 images, 10 videos, 10 audio clips, about
  50 materials; stability drops past roughly 8 distinct subjects.
- **Bind in prose.** `@Image 1 defines <subject>'s <appearance, clothing,
  structure, or material>.` `@Video 1 defines <motion, camera movement, or
  pacing>.` `@Audio 1 defines <voice, dialogue, ambience, or music>.` Put the
  exclusion in the same sentence: `Do not use the people in the image.`
- **Character sheets leak their staging.** Pair a sheet with `Do not take the
  grey backdrop, the panel borders, or the multi-view layout.`
- **Beats name characters, not handles.** `Mira, silver streak, rust-red jacket,
  crosses the stall line`, not `@Image 2 crosses the stall line`.
- **Several views of one subject must say so**, with the count: `All three
  images define one lamp. Exactly one lamp appears throughout.`
- **First and last frame.** Pass the `start_image` and `end_image` roles *and*
  state them in the prompt (`@Image 1 is the first frame …`, `@Image 2 is the
  last frame …`), one sentence per image. Same aspect ratio for both.
- Numbering follows upload order. `@Image 1` and `Image 1` are both accepted;
  use one form per prompt. See [multi reference](multi-reference.md) for the
  full binding workflow.

### Camera

Basic terms work directly: extreme wide, wide, medium, close-up, extreme
close-up; push-in, pull-out, pan, tilt, lateral move, follow, orbit, dolly zoom;
low angle, overhead, first-person; one-take, aerial, FPV, handheld. State shot
size, angle, movement, focus subject, and the transition. Motion matches the
action; it is not decoration.

- **Do not stack incompatible grammars.** `drone shot, handheld close-up,
  locked-off dolly, fast orbit` in one shot is the guide's named failure.
- With several subjects in frame, say **which** subject the camera follows or
  orbits, where the move starts, and where it ends.
- For a niche term, keep the term and describe the visible result:
  `Rack focus: the glass in the foreground softens while the face behind it
  resolves from blurred to sharp; no camera movement.`

### Audio and dialogue

Use the bracket syntax when tracks must be told apart: `()` music, `<>` sound
effects, `{}` dialogue, `【】` on-screen captions. Speech lives in the AUDIO
clause only; quoted subtext inside an action line comes back spoken. For
non-Chinese dialogue, state the language and delivery before the line:
`Dialogue language: American English. The courier says, low and flat: {We're late.}`

### Real-person characters

Seven slots: role, skin texture, facial details, eyes, hair, clothing and its
texture, body type and temperament. Write role, build, clothing, and action
rather than an age. Skin texture (pores, translucency, flush) is the slot that
most separates a photograph from a render. See [real person](real-person.md).

### The guide's prompt library

The guide ships ten tested prompt categories, each run across several
generations to find the structure that held. The example prompts and their
settings live on the page itself; this is the category list with the route
each one takes through this skill.

| Guide category | Skill route | Notes |
|---|---|---|
| Dramatic Exterior | T2V, or an I2V shot pair from a plate | Weather and time of day go in LOCATION; one camera move |
| Action Sequence | T2V, staged | Labelled shots with hard cuts; the PHYSICS line carries weight and impact |
| Commercial Product | R2V asset references | `@Image 1` is the product with a label exclusion; see the worked example below |
| Epic Landscape | T2V | Wide and extreme-wide sizes; aerial or FPV as the single camera grammar |
| Noir Scene | T2V | Lighting motivation and direction do most of the work; GLOBAL STYLE sets era and grade |
| Multi-Character Scene | R2V asset references | One reference per character, a non-interchange lock, beats that name characters rather than handles; see [multi reference](multi-reference.md) |
| Fantasy Action | T2V, or R2V with a style reference | PHYSICS for cloth, smoke, and liquid; one subject per camera move |
| UGC-Style Ad | R2V asset references, `9:16` | Handheld, first-person; AUDIO carries diegetic dialogue in `{}`. Higgsfield's bundled UGC workflows (`get_workflow_instructions`) are the alternative for talking-head formats |
| Horror Scene | T2V, staged | Vague transitions break tension fastest; an end state per shot; AUDIO names what must not be there |
| Documentary Style | T2V | Handheld, natural light, `No music` in AUDIO; the [real person](real-person.md) formula for subjects |

## Worked example: two-shot product beat, `omni_reference`

Inputs: `Image 1` is the product hero (imported with `media_import_url`),
`Image 2` is a kitchen plate. Parameters: `mode: omni_reference`, `duration: 8`,
`resolution: 1080p`, `aspect_ratio: 9:16`, `generate_audio: true`.

```text
GLOBAL STYLE: present-day lifestyle commercial, warm neutral grade, soft
contrast, no text overlays.
SCENE: a hand lifts the bottle from the counter and the label catches morning light.
@Image 1 defines the bottle's shape, label, and cap material; keep the label
text exactly as shown. Do not use the studio backdrop.
@Image 2 defines the kitchen counter, window, and morning light. Do not use
the people in the image.
LOCATION: the kitchen from Image 2, window camera-left, counter in the lower third.
FIRST FRAME AND BLOCKING: bottle centred on the counter, hand out of frame.

Shot 1 — medium close-up, eye level. A hand enters from the right and lifts
the bottle; condensation slides down the glass. Slow push-in.
End: bottle held upright at chest height, label facing camera. Hard cut.
Shot 2 — extreme close-up on the label, slight low angle. The bottle turns a
quarter turn toward the window; light sweeps across the label.
End: label fully lit and sharp, cap at the top of frame.

OPTICS: 50 mm equivalent, shallow depth of field, focus on the label.
CAMERA: one move per shot, no handheld shake.
PHYSICS: condensation runs with gravity; the hand's weight tilts the bottle slightly.
LIGHTING: key from the window camera-left, soft fall-off across the label.
AUDIO: <glass set-down, faint kitchen ambience>. No music, no dialogue.
Keep the label text exactly as in Image 1. Exactly one bottle throughout.
```

Preflight with `get_cost: true`, submit with `generate_video`, record the
`job_id`, wait with `jobs_wait`, and review the label first.

## Sources

- Higgsfield, [Seedance 2.5: Complete Prompting Guide (Full Prompt Library)](https://higgsfield.ai/blog/seedance-2-5-prompting-guide)
- Higgsfield, [Seedance 2.5 on Higgsfield in 2026: What You Get and How It Works](https://higgsfield.ai/blog/seedance-2-5-on-higgsfield-2026)
- Higgsfield MCP `models_explore` catalog, read 2026-09-21
- ByteDance Dreamina *Seedance 2.5 Prompt Guide* conventions (bracket syntax,
  role sentences, first/last-frame statements), as relayed by O-Side Media's
  MIT-licensed [higgsfield-ai-prompt-skill](https://github.com/OSideMedia/higgsfield-ai-prompt-skill)

## Related

- [execution adapters](execution-adapters.md) for the Atlas routes
- [model profile](model-profile.md) for the `higgsfield/seedance_2_5` capability layer
- [capabilities](capabilities.md) · [long video](long-video.md) ·
  [multi reference](multi-reference.md) · [editing and extension](editing-and-extension.md)
