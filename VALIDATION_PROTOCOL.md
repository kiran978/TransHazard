# Scientific validation protocol

## Label definition
For an environmentally documented parent → product transformation under a matching taxon, endpoint, and exposure duration, calculate molar response ratio `(C_product / MW_product)/(C_parent / MW_parent)`. The regression target is its base-10 logarithm. **EC50 and LC50 are never mixed.**

## Dataset v2 signoff
- Independently verify assay provenance, taxonomy, exposure conditions, effect estimate, uncertainty and censoring.
- Verify exact isomer/chemical identities, parent/product structures and transformation direction against source studies.
- Record separate reviewer decision, rationale, affiliation, review date, and verifiable signed source location.
- Obtain independent data steward authorization and freeze a versioned release. CSV metadata cannot authenticate reviewers on its own.
- Keep HOLD/EXCLUDE records outside training; preserve them in a versioned audit register.

## Model-readiness safeguards
- The supplied release gate uses conservative configurable engineering minimums: 30 distinct routes, 20 disjoint study-chemistry components, five source publications, and five held-out groups **within a single matched assay stratum**. These do not guarantee statistical sufficiency.
- Put connected study, route, CAS and canonical-isomeric-SMILES groups into the same partition.
- Select baseline versus ridge versus random forest using training-only group CV. Hold-out results are **internal**, not independently validated.
- Require external/source-independent validation, calibration, applicability-domain analysis, uncertainty intervals, and transparent baseline comparison before predictive claims.

## Current status
Six priority source-anchored observations from four routes; zero independently approved labels. Empirical model training is blocked. Synthetic software tests are not scientific performance evidence.
