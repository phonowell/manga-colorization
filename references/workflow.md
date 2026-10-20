# Execution guide

## Source inventory and ledger

Use stable work/chapter/image identifiers. Keep image index distinct from printed page number, including covers, spreads, interstitials, and original color pages. Lock the original path, dimensions, and SHA-256 before deriving crops. Preserve existing project data and use its schemas; do not replace a functioning ledger merely to match this guide.

Maintain these facts where they are needed:

| Record | Minimum useful content |
| --- | --- |
| Page/panel | Source binding, reading order, scene/time, actors, visible actions, occlusions, uncertain regions |
| Text/performance | Original transcription and location, speaker evidence, observed expression, inferred emotion separately; retain uncertain readings |
| Continuity object | Stable owner/object ID, state or costume, part colors, evidence source, page/panel appearances, exclusions |
| Color choice | Original color evidence vs user direction vs supplementary reference vs authored working RGB; lighting does not replace base identity |
| Candidate | Parent/source/input hashes, input crop/resize/padding, prompt, actual references, unchanged model result, served-file hash, review decision; preserve historical processing stages when diagnosing old candidates |
| Feedback | Exact reviewed hash, source coordinates and page dimensions, user's words, scope, status, later candidate binding |

Do not invent transcripts or claim exhaustive reading from a schema's presence. Record coverage and missing work. TTS preparation is optional metadata, not authorization to synthesize speech.

For corrections, reconcile the latest feedback, current mapping, and approvals per page and exact SHA. Preserve approved selections outside the rework scope. A page approved for one fix may later reopen for another defect; keep both decisions. Approval on one page does not close the remaining appearances of a cross-page issue.

### Japanese manga reading order

Read right to left through gutter-defined groups and finish each column before moving left where the layout calls for it. Verify dialogue exchanges against the original. Review [source-ledger correction](ledger-review.md) when auditing order, physical frames, narration/insets, spreads, text identity, or coverage. Geometry flags cannot replace native reading of the authorized range.

## Resolve before rendering

Check ambiguous regions against the original at native size, the surrounding panel, and adjacent original pages. A body part's ownership, outline, and motion sequence matter more than a crop's superficial shape. Prior model descriptions and colored candidates are hypotheses, not independent evidence.

Where uncertainty survives, make a small source-coordinate map: region ID, owner/material, confidence, evidence, and intended color. A loose rectangle locates an issue; it is not a safe paint mask. Keep unresolved areas separate. Do not hard-code a guessed interpretation into the permanent continuity ledger.

Select an intervention by mechanism:

- Correct model output with faulty publication: publish the already reviewed unchanged file through the explicit mapping when authorized; check served bytes before requesting another image.
- Correct model output damaged by historical processing: preserve the old stages as evidence; use the intact reviewed model file if suitable, otherwise ask the image model for a correction.
- Incorrect region meaning already in model output: correct the source reading and selected facts before the next model request.
- Correct meaning but inconsistent working color: supply the missing relevant owner/state palette and reference.
- Small confidently identified area: merge relevant feedback and preservation requirements, then use a full original page or its complete original panel as the model target. Inspect the final page after reconstruction.
- Ambiguous face/hand/hair intersection: resolve the source ownership first; a larger bounding box does not establish a boundary.

## Generation, panel assembly, and grading

Before new calls, inventory the complete panels already available from raw candidates, including rejected full pages. Track each proposed panel's source/candidate binding, geometry and lettering, semantic/color findings, and selection or rejection reason. If suitable panels cover the page, assemble and review it without another generation. For remaining work, choose unresolved complete panels/groups or a full page when context and layout call for it, carrying all applicable feedback and preservation requirements.

Read the available tool's actual image-size and input capabilities. The structural target may be a monochrome original page or a montage of complete original panels, including panels from different pages. Preserve source content and record preparation transforms and padding. Distinguish an artwork-generation montage from inspection-only sheets, overlays, and difference maps. Don't infer that extra resolution fixes meaning.

Plan multiple candidates as one bounded batch when panel selection is useful. If the provider returns one image per task, submit separate tasks together and record their batch identity; do not claim a multi-output response or silently discard provider outputs. Every candidate uses the original structural target, never a previous colored result.

For a panel montage, bind each slot to its original page SHA, full panel box, montage rectangle, and applicable palette/feedback. Keep independent panels visibly separate and identify their roles; packing does not make different pages one scene. Include whole balloons, lettering, and any elements crossing panel borders. If those cannot be separated safely, keep the relevant panels together or use the full original page.

Choose the least sufficient complete-panel group, not automatically the smallest rectangle. Retain neighboring original panels when they establish a back-view figure's identity, hair/garment ownership, or an action. A crop can preserve every pixel inside its box yet remove the context the model needs. Expand the source group when evidence supports context loss, rather than compensating with a guessed region description.

Keep raw generated files immutable. Check actual output slot positions, dimensions, borders, and lettering before extracting: valid preparation does not prove that the model preserved the montage. Reject material content drift rather than warping it into the intended box. Select complete panels that meet source, color, and semantic checks, then split and place them back using recorded coordinates. Save a manifest linking every final panel to its raw candidate SHA, extraction rectangle, destination rectangle, and any transform. A candidate can supply a valid panel while its other panels fail; the failed regions and whole-page decision remain recorded. Do not use tiny object patches or paint masks to replace model coloring.

Uniform whole-panel saturation, brightness, contrast, or similar grading is allowed. Record the operation and parameters, retain the pre-grade panel, and inspect the actual graded result for clipping, lost detail, and continuity. This does not authorize selecting hair, skin, mouths, or other semantic regions for code-painted color corrections. Wrong object ownership or missing pigment goes back to the model.

Use a representative reference set suited to the work. If the user specifies four original color pages and the preceding page, honor that; the number is a project choice, not a universal requirement. Avoid redundant references. Review reference conflicts before calling; don't conceal known faults in the preceding page.

Compile the actual request from selected live owner/state facts as described in [request preparation](request-packet.md). Bind required facts, reference versions, and prompt to the inputs; recompile after any locked dependency changes. Do not reuse withdrawn region notes from historical prompts.

Keep each stage as a new artifact. Save actual requests and results without credentials, tokens, or cookies. Record failed calls and rejected artistic results as different outcomes. Counts and reported usage are facts; absent monetary prices stay unknown.

Save the model result unchanged. Inspect selected panels and the actual assembled/graded page, local contours, lettering, tonal fields, and adjacent continuity. Include retained panels in this final review: an earlier pass or focus on a different defect may have missed altered eyes or text. A global alignment score can miss small facial errors. Ask the image model to repair missing or misplaced object colors and content changes; complete-panel selection may avoid a defective panel without painting over it. Preserve the user's ink-tint and effect-lettering choices in the request.

## Inspection bundle helper

Python 3 and Pillow are required. Use the environment already available for the project; the helper never installs packages. Paths in a plan resolve relative to the plan file. Native crop coordinates are `[left, top, right, bottom]`, exclusive at right/bottom. Each stage has its own coordinate system; a raw generated image must not be cropped with source coordinates without the recorded transform. Use concise ASCII stage captions such as `Original`, `Raw`, and `Composite` for the contact sheet. A multilingual `label` may include an explicit ASCII `stage`; full labels remain in the manifest.

Example plan:

```json
{
  "purpose": "Compare the reviewed mouth with its original",
  "items": [
    {"label": "Original", "path": "original.png", "crop": [40, 20, 100, 80]},
    {"label": "Reviewed candidate", "path": "candidate.png", "crop": [40, 20, 100, 80], "sha256": "<actual reviewed SHA-256>"}
  ]
}
```

Run:

```sh
python /path/to/manga-colorization/scripts/inspect_bundle.py --plan /path/to/inspection.json --out /path/to/new-evidence-directory
```

The directory must not exist. Input errors, hash mismatch, and out-of-bounds crops fail before writing it. The output contains the exact plan, per-input hashes/dimensions/crops, native crops, and a labeled contact sheet. The sheet enlarges/reduces crops only for comparison; inspect saved native crops for edge quality. Hash binding proves which bytes were inspected, not semantic correctness. Do not include private material in a bundle intended for sharing.

## Delivery and handoff

Keep the current image mapping distinct from immutable generation directories and the formal release selection. Bind model corrections to original hashes; keep raw outputs, assembly manifests, grading parameters, and final files as separate artifacts. Historical code-painted pipelines remain historical; their existence is not permission to resume object recoloring. Review the actual final page, native risk regions, and adjacent sequence. Record final SHA, observations for each quality dimension, remaining uncertainties, and host/user status separately. A prior review expires when pixels change. Update the mapping atomically after reviewing the actual final file and within existing authorization. Check that the review page serves that file's bytes; thumbnails and cached URLs are not sufficient evidence. Do not restart a user's service to refresh images.

For a chapter delivery, include source-ordered pages and a manifest of selected filenames/hashes. Check archive readability, count/order, native dimensions, and equality with selected candidates. Preserve earlier releases. Note unresolved issues and distinguish working candidates from accepted pages.

Handoff must identify the latest source of truth, open semantic questions, failed attempts and their mechanism, invocation counts/unknown costs, what was actually inspected, remaining work, and the next bounded action. Avoid copying entire conversation histories into reusable instructions.

When explaining how a correction was made, state the actual model calls/candidates, reused panels, assembly and uniform grading, and final review status. Distinguish an unchanged model output from a panel assembly. Once an eligible candidate is published for user review, leave it pending rather than continuing speculative generation.
