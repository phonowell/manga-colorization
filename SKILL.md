---
name: manga-colorization
description: Color existing manga, maintain character and prop continuity, review source reading order and ledgers, and diagnose coloring regressions. Use for manga coloring, recoloring, source-ledger review, or color review; not for drawing new panels or general illustration.
---

# Manga colorization

Deliver coherent color artwork whose shapes, acting, and reading sequence remain grounded in the manga original. Treat visual quality as the outcome; generation success and geometric registration are supporting evidence only.

In Colorleaf, the image-generation model supplies object colors and fixes missing or misplaced pigment. Code must not replace this work with object masks, fills, or pixel recoloring. Code may generate multiple candidates, pack complete original panels from one or several pages for a model request, split results back out, assemble complete panels selected from candidates, and apply uniform whole-panel adjustments such as saturation or brightness. Preserve raw outputs separately and record assembly and grading provenance. Inspection overlays and difference maps remain evidence only.

Use the monochrome original as the structural authority: either a full page or a source-bound montage of complete panels. Never edit a colored candidate or chain model outputs; colored pages supply color references only. Consolidate feedback by page and panel: a full-page request includes all valid page feedback; a panel request includes all valid feedback and preservation requirements for those panels. Multiple candidates share the applicable requirements. Review the final assembled page as well as its panels. Historical feedback boxes stay attached to their reviewed SHA, not to a newly generated image. See the [execution guide](references/workflow.md) for panel packing, selection, and reconstruction.

## Select the work

- **New chapter:** read the requested source range, establish continuity evidence and uncertain regions, then pilot representative pages before batching.
- **Correction:** bind feedback to the exact reviewed image and original, preserve approved selections, and inventory reusable candidate panels before requesting more images. Locate the earliest failing stage, then choose the original page or a complete-panel group with enough semantic context.
- **Source or ledger review:** read [source-ledger review](references/ledger-review.md) for reading paths, coverage, semantic withdrawals, and synchronized corrections. Review the authorized range, including pages without geometry warnings.
- **Repeated rejection:** suspend retries on the affected pages, compare prior interpretations and intermediate artifacts, and repair the diagnosis before generating again.

Read only the references needed for the task:

| Task | Reference |
| --- | --- |
| Inventory, generation stages, inspection bundles, delivery | [Execution guide](references/workflow.md) |
| Compile a new request from live facts and locked inputs | [Request preparation](references/request-packet.md) |
| Diagnose rejection or evaluate a changed method | [Diagnosis and evaluation](references/quality.md) |
| Audit source reading, stable identities, or derived ledgers | [Source-ledger review](references/ledger-review.md) |
| Check the source-preservation publication gate | [Pixel-coordinate source fidelity](references/pixel-fidelity.md) |

Project progress and candidate decisions live in Colorleaf's current-status document and live ledgers, not in this reusable skill. Do not require a full chapter reread or an experiment suite for an uncomplicated local correction.

## Preserve the authority and the uncertainty

- Original manga determines geometry, expression, eye state, lettering shapes, and scene contents. Original color pages determine color where applicable. User corrections take precedence over agent interpretations. Anime and generated references are supplementary, with their provenance recorded.
- Separate source observations, agent hypotheses, authored RGB choices, model proposals, and user decisions. An uncertain sleeve, cheek, hair strand, or sky opening stays uncertain until examined; a confident prompt does not settle it.
- Identify who owns each visible part before assigning an object's palette. Apply facts only to parts visible in the source state: a character's normal iris color must not introduce pupils into closed or empty-circle eyes. Motion repetitions, exaggerated white eyes, speed lines, blank shapes, and dense tones are not reliable semantic boundaries by themselves.
- Use a persistent ledger across pages. The model sees only the supplied inputs, not the ledger or the conversation. The previous colored page supports continuity but can itself be wrong.
- Withdraw a disputed active interpretation at its authoritative record, and update current summaries and derived inputs that repeat it. Preserve history as superseded. Do not forward a historical claim because its old prompt or README still sounds certain.

## Make the smallest supported intervention

For each attempt, identify the observed loss, suspected stage, intervention, relevant comparison, and stopping condition. Prefer reusing valid complete panels over rerunning the provider. A planned batch may contain multiple candidates for panel selection; record its size before submitting and inspect them together. One diagnostic batch per distinct intervention is a useful default, not a one-image limit. Repeated failure of the same mechanism triggers diagnosis rather than an unbounded sampling loop, even with unlimited generation authorization.

For a genuinely ambiguous panel, inspect enough original context to establish ownership; the smallest crop may remove the evidence needed to read it. Record unresolved ownership in a source-aligned region map where useful; a needed visual study must use the image model. Keep unknown areas marked internally. Only then ask for pigment, lighting, and paper texture. Normal readable panels do not need manual segmentation. If uncertainty materially prevents a correct result, present the exact unresolved crop for clarification after independent evidence is exhausted.

## Keep generation inputs economical

Supply the correctly sized original, relevant original-color references, the actual immediately preceding colored page when continuity is requested, and the minimum verified palette/occlusion information. List image roles explicitly. Use exact RGB for working colors; allow shading and medium variation. A concise prompt skeleton is:

> Color Image 1 only; preserve its drawing, panel layout, pose, expression, and eye state. Image 2 supplies color and paper texture; Image 3 supplies page continuity. [Relevant RGB palette.] [Only a verified difficult-region clarification if needed.]

Respect the user's intended saturation and medium. Do not inject debugging history, ledger mechanics, unsupported region assertions, every panel's synopsis, or instructions intended for the host. Preserve the effective prompt and actual input hashes; never silently run a prompt rewrite. Use the available authorized generation tool without changing provider settings or assuming this skill grants paid-call authorization.

Select required owner/state facts before compiling the request. Missing required facts and unresolved material boundaries block that request; do not resolve them by omitting the declaration. `scripts/prepare_request.py` supports the documented prepared-page format and rejects unverified region notes or stale dependencies. It cannot infer fact coverage or establish source meaning. For other tools, preserve these bindings with their actual request format rather than inventing a compatibility layer.

## Separate preservation from quality

Inspect the original, raw model outputs, panel assembly and any whole-panel grading, and the served file. Locate losses at the stage that introduced them. Permission for complete-panel assembly does not authorize code to paint an object or fill its missing color. Source-line alignment can coexist with wrong object colors. Never treat a closed white component as a semantic object or a speech balloon without corroboration.

Keep structural ink separate from screen-tone density, mood, speed lines, and decorative lettering. Translate those marks into intentional colored values appropriate to the chosen medium; do not multiply monochrome shading back indiscriminately. Do not remove intentional dark hair, pupils, or clothing merely because it is dark.

## Review and leave recoverable work

Inspect both the complete page/adjacent sequence and native-size risk areas, including retained panels from earlier candidates. Evaluate source fidelity, semantic boundaries, continuity, color completeness, and aesthetic finish separately. Ask the image model to preserve good regions when correcting others, then open and review the actual saved result. A passed crop does not approve the whole page. Bind the review to that final file's hash and record unresolved findings. Record failures and regressions alongside improvements.

Publish only the candidate actually reviewed; keep its exact image hash and original binding. Feedback remains attached to its reviewed version. A host-reviewed candidate is not user-approved; once ready for user review, stop generating for that correction. Bind approval to the selected page version, not every page of a cross-page issue. On new feedback or rejection, reopen the affected issue, supersede disputed active interpretations, retain their history, and make the rejected state visible without silently swapping to another bad image.

Source preservation is a pre-publication gate: use [pixel-coordinate source fidelity](references/pixel-fidelity.md). Calibrate tolerances from the user's accepted pages, allowing normal raster/line-width/texture variation. Preserve content and acting; whole-page similarity cannot hide a changed glyph, expression, or gesture. Comparison uses fixed source coordinates; diagnostic alignment cannot make a result eligible. Metric alerts require visual diagnosis, not automatic artistic rejection or approval.

For reproducible inspection, use `scripts/inspect_bundle.py` with an explicit JSON plan. It reads local images, locks hashes, and writes an immutable contact-sheet bundle; it does not generate, classify image content, or publish. See the execution guide for the plan format. Verify delivery ZIP contents against the selected candidate hashes before describing them as current.
