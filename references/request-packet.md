# Bind live facts to a generation request

Use this before a new generation request, including after a rejected interpretation changes. The host still reads the original and decides which facts are necessary. The helper checks declared facts and file versions; it cannot recognize a sleeve, prove complete palette coverage, or approve artwork.

## Select facts first

From the page's visible owners and costume/prop states, select the working colors the model needs. List these as `requiredFactIds`, then resolve each from the live authoritative ledger. Keep evidence and hypotheses in the ledger; pass only useful RGB labels and verified difficult-region notes to the image model. A label must locate the right owner and part, not repeat a disputed interpretation.

Scope palette facts to the visible part and source state. A closed eye or an exaggerated empty circular eye has no visible iris to color; supplying the character's normal iris RGB can contradict the drawing. Keep that palette fact in the ledger but leave it out of this panel's request, recording why it does not apply. Conversely, keep necessary visible-part facts even when inconvenient to compile. Audit the effective prompt and reference images for these contradictions before adding more preservation instructions.

Save a concise host coverage review in the packet's optional `coverageNotes`: visible owner/state → selected facts, plus intentional white/dark parts and unresolved omissions. This stays out of the image prompt. The helper locks the packet's bytes but cannot certify the coverage note; declaring only skin does not prove a visible costume or prop has been covered.

Keep a material boundary in `unresolvedRequired` if it is necessary for the requested correction but remains unclear. Do not clear that list merely to obtain a runnable request. Resolve it against the original context, or prepare a source-aligned region study. When an interpretation is withdrawn, update its active status and current projections before preparing another request; preserve the old claim and its prior inputs as history.

## Supported prepared-page format

`scripts/prepare_request.py` is a local compiler for the existing `plan.json` / `input.json` page-preparation format. It requires Python 3 and Pillow in an existing environment. It never calls a provider, installs dependencies, or changes provider configuration. Other generation tools can use the same principles without adopting this adapter.

This existing adapter supports a full-original-page target. It checks that `input.json` names the same original path/SHA as `plan.source`, that content dimensions remain unchanged, and that decoded content pixels equal the original with only declared nonnegative padding. It refuses colored edit bases, rescaling, and altered content. In Colorleaf the original must be monochrome; the host remains responsible for source meaning and reference roles. This adapter limitation does not prohibit the authorized complete-panel montage workflow in the [execution guide](workflow.md). A panel-capable request path must validate each slot against its source crop and record the extraction/reconstruction map; do not forge a full-page binding or weaken this adapter's checks to submit a montage.

The prepared directory contains:

- `plan.json`: `source` with `id`, `path`, `sha256`; `canvas` width/height; `targetPreparedSha256`; `referencePreparedSha256`; and `additionalReferences` with `file`, `role`, `sourceId`, `usedPath`, `usedFileSha256`, `preparedSha256`.
- `input.json`: `originalPath`, `originalSha256`, `scaledContent` width/height, and four `padding` offsets.
- `target-prepared.png`, `reference-collage.png`, and each additional reference file. The target preserves original content at its native size with recorded padding; compilation does not resize or repaint it.

This adapter expects numbered source IDs such as `work/0001/0008.jpg` and exactly one `previous-page.png` bound to source `work/0001/0007.jpg`. It fits workflows requiring an actual preceding page; it does not support a chapter's first source image without one. It does not infer a correct preceding image from the filename. The host must supply the actual selected file. Additional reference roles are host-authored prompt text and must be concise.

For a diagnosed reference-interference experiment, `referenceMode: "source-only"` must be explicit in both packet and prepared plan. This mode uploads only the unchanged full original: `additionalReferences` must be empty and `referencePreparedSha256` absent. Supply nonempty `coverageNotes`, all required palette facts and merged feedback; no visual continuity is claimed. The compiler still locks the original, source pixels, feedback and selected ledger values. Default requests keep the preceding-page checks above; an omitted reference is never silently treated as source-only. A failed experiment still triggers the skill's diagnostic stopping rule.

Example packet; paths resolve relative to the packet file. IDs and JSON pointers below are illustrative and must match the actual ledger:

```json
{
  "preparedDirectory": "prepared-page",
  "currentImagesPath": "current-images.json",
  "selections": [
    {
      "id": "hero:outdoor:skin",
      "kind": "palette",
      "ledger": "continuity.json",
      "pointer": "/objects/0/parts/skin",
      "label": "主人公面部、耳朵和手部肤色"
    }
  ],
  "requiredFactIds": ["hero:outdoor:skin"],
  "unresolvedRequired": [],
  "style": "鲜艳通透的纸上水彩，保留纸质笔触，墨线可随材质染色。"
}
```

Palette pointers must resolve to three integer RGB values in 0–255. A `region` selection instead resolves to an object with a nonempty `note` and explicit `status` of `verified` or `user-confirmed`. Missing, unresolved, or withdrawn status is refused; the host must actually verify the interpretation before changing that status. Repeated or missing required IDs are refused.

When a project has a current mapping, supply `currentImagesPath`. It contains `entries` with `sourceId`, absolute `path`, and `sha256`; Colorleaf also records explicitly retained versions in the disjoint `retainedSelections` array in the same file. Together they are the complete mapping. The helper requires exactly one entry across these arrays for the preceding page and rejects a reference whose path or SHA differs; missing entries never fall back to a historical selection. Colorleaf uses this mapping for both first chapters, review and export. Hash checks bind bytes, not the claimed page identity, collage quality, or approval status.

For same-page corrections, an optional `mergedFeedback` object with `path` and `sha256` locks the merged feedback file as another dependency. The host must still reconcile current feedback, preservation requirements and source-bound annotations; a file hash does not establish semantic completeness.

## Prepare, inspect, execute

```sh
python /path/to/manga-colorization/scripts/prepare_request.py prepare --packet /path/to/packet.json --out /path/to/new-request-directory
python /path/to/manga-colorization/scripts/prepare_request.py verify /path/to/new-request-directory
```

The output directory must not exist. The compiler copies prepared inputs, compiles a short prompt with image roles and selected facts, updates its prompt hash, and writes `request-readiness.json`. The new plan drops the template's historical `authorization` field and marks itself as prepared, not generated or reviewed. Existing authorization must come from the current task context; this does not revoke authorization already given by the user. It locks the packet, compiler, live ledgers/mapping, original, prepared artifacts, prompt, and new plan by absolute path and SHA-256. A changed dependency requires rebuilding from current facts in a new directory; never edit hashes merely to pass verification. Historical packages may no longer verify after a live ledger change; retain them as historical evidence.

Review the actual prompt and supplied images before invoking the authorized generation tool. Required facts are a host declaration, not automatically inferred from appearances. Free-text labels/style/reference roles are also host decisions; the compiler does not validate their meaning. Keep the source and reference roles correct and omit production history. The readiness file establishes input consistency only; authorization and output review remain separate.

For a runner that consumes this format, verify readiness immediately before task creation/provider setup and fail before sending when it is absent or stale. An old prepared directory must be recompiled, rather than adding an empty readiness file. This skill's helper cannot enforce an unrelated runner that ignores it. In the current two-chapter Piexl experiment, `generate-page.ts` enforces this check before writing `request.json` or loading provider configuration.

Multiple candidates may be prepared and submitted as a planned batch with the same applicable facts and feedback. Each task must retain its actual prompt, input hashes, output, and batch identity; a single-output provider can use parallel tasks without claiming native multi-output support.

Colorleaf also provides `scripts/prepare-panel-model-rework.py --packet PACKET --out NEW_DIRECTORY`. This separate source-only path declares `source.kind: original-panel-montage`; it does not pretend to be a registered full page. Its packet binds the source registry and merged feedback, canvas, batch identity, and each complete panel/group's original SHA, source box, destination, boundary review, applicable feedback IDs, and ledger fact pointers. It validates original monochrome pixels, bounds, non-overlapping slots, exact crop copies, applicable feedback coverage, and locked dependencies. The host still verifies complete-panel boundaries, source meaning and relevant fact coverage. The output uses the existing runner's readiness format and Provider. Preserve a separate reconstruction manifest when selecting output panels; a valid input montage does not establish that the model retained its slot positions.

This montage path requires at least one slot and RGB ledger values of three integers in 0–255. Paths resolve relative to the packet file, including source-registry image paths; fact addresses use RFC 6901 JSON pointers, as in the full-page compiler.

After generation, save raw model results unchanged and follow the execution guide for review. Code may split and assemble complete model-colored panels and apply uniform whole-panel grading; retain the constituent hashes, coordinates, and grading parameters. Open the **actual final page**, inspect its native risk areas and adjacent sequence, then record its SHA and observations. Missing or wrong object colors still go back through the image model, never code fills. Mechanical readiness is not a substitute for final review and is not a publication action.
