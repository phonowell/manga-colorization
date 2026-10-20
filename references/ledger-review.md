# Source reading and ledger correction

Use for checking an existing manga reading, correcting its ledger, or resolving a disputed interpretation before coloring. Keep book-specific discoveries, page lists, and one-time apply scripts in local project evidence.

## Establish the scope and coverage

Read the current handoff and remaining-page queue. Bind observations to source ID, original SHA, and the ledger revision being reviewed. Preserve a before snapshot. Scope a single-page correction locally; for an authorized range review, work through that range in batches, including unflagged pages. Geometry warnings prioritize inspection; their absence provides no evidence that order or semantics are correct.

The Colorleaf repository's `scripts/audit-reading-order.py` can freeze a local inspection bundle and flag possible reversals. Creating that bundle does not perform a visual review or correct any ordering.

Record coverage separately for contact-sheet overview, native original reading path, selected verbatim text, semantic/ownership checks, candidate image quality, and user approval. Mark only what was actually viewed or checked. A full-page native view does not certify every tiny label, speaker, or object. Historical inspection booleans are previous claims, not the current reviewer's evidence. Deduplicate overlapping batches by source ID and SHA; a changed original needs a new binding. Keep remaining pages explicit, and resume that queue when continuing.

## Read the composition before ordering records

For Japanese manga, read right to left through the groups established by gutters, then downward within each group. A right column of two frames can finish before a tall frame to its left. Confirm the path against opening lines, replies, balloon tails, and actions. Do not globally sort boxes by top edge or reverse characters inside a Chinese phrase or Latin label.

Distinguish stable ledger regions from physical frames. Several old regions may cover one continuous frame; one old region may straddle several frames. Record this correspondence without renaming IDs merely to obtain a clean panel count. A narration rectangle is not necessarily a narrative frame, and a full-page background is not necessarily a later event. Correct stale locators where supported, retaining uncertainty about fine outlines; rectangles are not paint masks.

Keep main dialogue, narration overlays, and independent illustration labels distinct when they do not form one serial path. Record an inset-and-return path with explicit text references, such as background text A → inset text B → background text C. Costume examples, profile columns, diagrams, and accompanying effects need navigation or association, not invented event times. A flattened panel order alone cannot encode every path.

Inspect suspected spreads together, left half on the left and right half on the right. Check seam continuity and text continuation, retain source-file sequence, and record each half and its partner. Covers and illustrations also need this check when their composition suggests a spread.

## Verify meaning and text independently

Read a difficult crop with its whole page and adjacent originals. An apparently mechanical shape may be a transforming prop; a face-like marking may belong to a hand or object. Existing generated images, old prompts, and repeated ledger descriptions are not independent corroboration. Withdraw disproved actors, props, ownership, and plot claims at the active record rather than merely adding a warning elsewhere.

Check speaker evidence separately from transcription and ordering. A nearby silhouette, inferred age/gender, or word such as “sister” does not establish who speaks or who accuses whom. Use balloon tails, group positions, and adjacent exchanges; leave the local or canonical speaker unassigned when the evidence does not resolve it. Keep uncertainty about a speaker even if the sentence is clear.

Inspect the whole balloon before splitting or merging text. A sentence-final exclamation may continue the same balloon; exterior cries may be accompanying effects. Do not repair tiny brands, distorted speech, or Japanese effects from expectation. Preserve partial/unreadable status until the original supports a transcription, and never turn a guessed effect count into verified coverage.

A legacy text record can combine a main balloon with another character's nearby aside. Verify each unit's speaker before retaining it as one text; a supported split needs separate speaker evidence and identity lineage. Correct negation and numbers at the specific sentence and its repeated summaries, checking neighboring sentences independently rather than globally replacing the same word or numeral.

## Apply a recoverable correction

Keep reading positions separate from identities. Before reordering, bind text IDs to their existing records using the repository's identity rules; old global text numbering and outside-text array positions may differ from current reading order.

- **Reorder:** retain IDs, change positions, and update dependent transition explanations.
- **Merge:** keep an explicit surviving ID; retire the others with their original content, reason, and successor reference. Do not reuse a retired ID for a different phrase.
- **Split:** retain the original ID for the supported continuing unit, add an ID for the separated unit, and record the lineage and reason.
- **Withdraw:** preserve the old claim as superseded evidence; remove it from active interpretations and derived candidates. If useful, add a separately identified unresolved region without claiming its old labels or count were verified.

Update the effective reading, active plot summaries, speaker/identity overlays, candidate indexes, and current read-book notices that repeat the changed claim. Preserve historical bodies and source hashes. Rebuild indexes using stable identities and preserve their existing selection rules and unrelated annotations; collecting every non-dialogue kind is not equivalent to maintaining an existing effect index. Reconcile additions/removals rather than forcing counts to remain constant.

One character can appear repeatedly within a single ledger region as motion, memory, or a display overlay. Preserve each appearance and its locator: an index keyed only by local character ID can silently overwrite an earlier appearance. Compare candidate records with their occurrence/region identity and multiplicity, while keeping the shared character identity.

Read the latest files before applying. If another session changed unrelated fields, preserve that latest revision and merge the supported correction. If the source or relevant reading changed, reconcile before applying; do not overwrite with the old snapshot. Snapshot relevant current projections and compare again before writing. Runtime mapping/history drift is not permission to reset them; record externally changed files separately from files proven unchanged. Do not publish or change image selections as a side effect of ledger review.

## Verify and hand off

Check the affected schema, original hashes, identity lineage, route references, and index equivalence for candidate contents, current positions, and locators. Check unchanged sources/projection entries and protected feedback/history separately. Preserve historical artifact bytes; if a legacy declared digest predates migration rewriting, state which actual snapshot hash was compared rather than silently rewriting history or claiming the old declaration matched.

Report what each result establishes: schema and hashes prove structural/file integrity; original viewing supports the specified reading or semantic observation; neither proves exhaustive transcription, artwork quality, or user approval. State inspected and remaining ranges, unresolved microtext and ownership, current authoritative paths, and the next batch. Keep one-time apply scripts marked as already executed. Record technical failures and corrective follow-ups without rewriting earlier evidence as if it had been correct initially.
