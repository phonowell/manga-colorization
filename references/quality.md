# Diagnosis and evaluation

## Find the first loss

Compare the same native region through original → prepared page/panel montage → raw model result → selected panel/whole-panel grade → final served page. Inspect preserved stages to locate the first loss. Complete-panel assembly and uniform panel grading are permitted; code-painted object colors remain prohibited. Write observations before proposing causes, and inspect input/output coordinate differences explicitly.

| Observable evidence | Interpretation to test | Appropriate intervention |
| --- | --- | --- |
| Same wrong part color already in raw output | Source interpretation, prompt/reference conflict, or model semantic error | Compare original context and effective input; resolve region meaning before another call |
| Ownership fails after isolating a panel | Crop removed identity, garment, or action context | Compare the original sequence; include the complete neighboring panel/group that supplies the missing evidence |
| Palette is correct for the character but the visible state changes | Inapplicable fact conflicts with source state | Scope facts to visible parts, such as omitting iris RGB for closed/empty-circle eyes; preserve necessary visible-part facts |
| Input montage is exact but output slots move or text changes | Model changed layout/content after preparation | Inspect actual output geometry and lettering before extraction; select another valid panel or change the source group, without warping away drift |
| Different rejected pages/candidates contain all needed valid panels | Full-page status obscures reusable constituents | Review complete panels individually, assemble them with provenance, and inspect the final page before making more calls |
| Model result is correct but a historical composite bleeds | Registration, stroke removal, or resampling | Inspect preserved stages; use the intact reviewed model file if suitable, or request model correction |
| White fringe appears at a historical paint-mask boundary | Threshold support omitted antialias/gray pixels | Inspect the saved mask and source ink for diagnosis; correct artwork through the image model |
| Patch affects only some material occurrences | Missing owner/state mapping or too narrow correction scope | Trace the same object through source sequence; don't globally recolor all similar-looking pixels |
| New color becomes gray/dirty after historical compositing | Source tonal density may have been applied twice | Compare existing raw and composite artifacts; preserve the finding and use model output/correction |
| File is correct but review still shows older pixels | Publication mapping/cache/version binding | Compare served image bytes; do not generate a new image |
| Selected panel differs from the assembled page | Different constituents, transforms, or grading | Inspect saved hashes, rectangles, and grading parameters before blaming color generation; correct the mechanical stage if it caused the loss |
| Repeated rejection despite alignment/support checks | Criteria omit semantic or aesthetic losses | Reopen the interpretation and review the whole image; don't relax checks or continue an unchanged retry loop |

These are diagnostic hypotheses until the stage comparison supports them. More than one mechanism can coexist. A visible defect found by the agent is not automatically the full explanation for an unspecific user rejection.

## Design a bounded intervention

Before a model correction request, record:

- Observed failure, bound to source and candidate hashes.
- Causal hypothesis and the evidence that could disprove it.
- One meaningful intervention; keep unrelated inputs fixed where feasible.
- Intended improvement plus what must remain intact, at native size and in page sequence.
- Number of attempts and stop condition; do not reinterpret failed attempts as requests for more samples.

Default to one bounded diagnostic batch per mechanism. A batch can contain multiple candidates for complete-panel selection; set its size before calling and compare all results. This is not a one-image limit or a requirement that every panel come from one candidate. If the same loss persists across the batch, inspect before proposing another intervention. Unlimited billing authorization removes a financial ceiling; it does not make blind retries useful. Comparing existing artifacts and correcting ledgers needs no provider call.

## Quality dimensions

For Colorleaf's source-preservation gate, read [pixel-coordinate source fidelity](pixel-fidelity.md). Compare at original coordinates and calibrate normal variation against the user's accepted chapter. Metric alerts direct native inspection; benign line-width, antialiasing and texture changes are tolerable. Confirmed changes to text content, expression, gestures or material object geometry reject the candidate regardless of color improvements. Separate measured diagnostics, host judgment and user approval; do not call an ordinary visual check pixel-exact certification.

Review dimensions separately rather than hiding failures in a single average:

1. **Source fidelity:** panel borders, silhouettes, original strokes, gesture, eye/mouth state, no invented anatomy or scenery.
2. **Semantic boundaries:** each visible face/ear/hand/hair/garment/prop/background belongs to the right object; tears and gaps remain correctly interpreted.
3. **Continuity:** identity, costume state, props, recurring environment/light and sky treatment through the actual sequence.
4. **Color and finish:** requested saturation, distinct skin, material/paper texture, intentional effect colors, no dirty double tones, halos, hard patch seams, or lost detail.
5. **Delivery integrity:** exact candidate/version binding, original-size image, review freshness and archive contents.

A generic pixel-difference test cannot validate semantic boundaries. Matching source ink cannot prove correct anatomy when generated broad color shapes remain underneath. Conversely, permitting colored lines means pixel equality with black source strokes is not the artistic criterion.

## Improve without overfitting

Keep development/regression pages separate from held-out pages. Any page used to design a prompt, mask, or new rule is development material, including its crops and variants. Validate a changed general method on held-out material with different panel density, tonal/line treatment, acting and occlusion mechanisms; a renamed character is not independence.

Compare against the previous method on the same validation inputs. Include normal areas that should remain unchanged and intentional dark/blank regions that should not be 'fixed.' If only the original regression is tested, report only that result. Keep ambiguous outcomes and user disagreement; never promote host self-review to user approval.

Only move demonstrated reusable mechanisms into the skill. Keep character-specific RGB, book-specific panel identifications, provider settings, and one-off masks in the project's ledger. Repeated contradictory descriptions are a reason to remove an active assertion and record uncertainty, not to append more prohibitions.

Before another prompt revision, audit source context and contradictions among selected facts, references, and preservation requirements. A longer list of forbidden mistakes is not a new causal intervention. Distinguish an observed improvement after a changed input from a confirmed cause. Do not universalize a successful batch size, montage layout, or page-specific instruction; set batch size for the current selection task and keep calibration fixed while evaluating it.

Maintain concise evaluation evidence with scenario, permitted actions, actual decision/artifact, failures, and limits. A skill/frontmatter validator establishes packaging only. A realistic dry run establishes the particular behavior observed; it does not establish world-class artistic quality or automatic reliability.
