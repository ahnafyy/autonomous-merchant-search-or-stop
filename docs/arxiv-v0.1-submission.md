# arXiv v0.1 Preparation Record

## Scope

This branch prepares, but does not submit, the `v0.1` preprint for *When Should a
Shopping Agent Stop Searching?* The intended evidence release reports the verified
two-snapshot catalog-search analysis and its registered claims. Its primary policy is
commit-or-continue: continuing does not reserve an earlier catalog offer.

Daily panel re-observation and weekly discovery are ongoing. Their raw outputs are
operational provenance for a later longitudinal analysis, not evidence or findings in
the intended `v0.1` results. Retained-offer and revalidation policies are also outside
the current evidence release; they need a recall-aware benchmark before they can be
reported as results.

Future conference submissions may revise this work after sufficient longitudinal
observations support additional analyses. They are future plans, not submission or
acceptance claims.

## Release Checks

Choose and record a collection cutoff before creating the arXiv source archive. Run
these from the repository root against that frozen, validated working tree:

```bash
.venv/bin/python -m paperkit.cli validate --release
.venv/bin/python -m paperkit.cli build
.venv/bin/python -m paperkit.cli build-paper
```

The resulting PDF is `dist/paper.pdf`. The source archive must include the manuscript
sources, generated `paper/generated/` inputs, and the generated bibliography, but not
local virtual environments, output PDFs, credentials, or live collection outputs that
are still running. Raw ongoing collection data remains in the repository unless it is
deliberately evaluated and registered for a later release.

## Manual arXiv Submission

1. Create the source archive from the validated working tree.
2. Upload it through the author's arXiv account under the category recorded in
   `project.yml`.
3. Confirm that arXiv's compilation preview matches `dist/paper.pdf` and that all
   citations and tables render.
4. Record the arXiv identifier and submission date in a follow-up release commit only
   after arXiv assigns them.

## Future Conference Revisions

Before revising for a conference, regenerate and evaluate the accumulated daily panel
series. Add only analyses with registered claims and executable evaluators; do not
retrofit results into the v0.1 preprint.