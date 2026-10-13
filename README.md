# TransHazard

**Parent → environmental transformation-product aquatic toxicity change**

**Scientific status: Dataset v2 NOT APPROVED; empirical predictive model NOT TRAINED.**

This repository develops a reproducible workflow for the original TransHazard research question: quantify and predict toxicity changes between a parent chemical and its documented environmental transformation product, within a *matched species, endpoint and exposure duration*.

The regression target is:

```
delta_log10 = log10[(C_product/MW_product) / (C_parent/MW_parent)]
```

where both concentrations are consistent mass-per-volume EC50 or LC50 measurements. Positive values denote reduced toxicity of the product by that assay's point estimate; negative values denote increased toxicity. LC50, EC50, species and durations are not interchangeable.

## Current evidence release gate

- 33 screened route hypotheses (not all source verified).
- Six high-priority *unapproved* assay observations across four routes, three publications, three chemical networks and five assay contexts.
- **Zero independently approved Dataset v2 labels.**
- Insufficient independent matched parent-product assay groups for a defensible held-out model evaluation.

Never present synthetic code tests, screening matches or fitted publication endpoints as validated model performance or independent signoff.

## Planned structure

```
run_pipeline.py              # CLI: audit, guarded train
src/transhazard/core.py      # molar change, human-review gate, grouped model development
tests/                      # scientific gates and synthetic-only smoke test
data/                       # unapproved candidates and empty approved-release schema
.github/workflows/ci.yml    # automated checks
VALIDATION_PROTOCOL.md      # scientific review and validation standards
```

## Next scientific steps

1. Independently adjudicate source-anchored parent-product pairs and reconcile original studies.
2. Expand diverse, assay-matched and independently documented transformation routes.
3. Freeze Dataset v2 with authenticated scientific approvals and verified structures.
4. Run grouped model development and **independent** external validation only when feasibility gates pass.

**Data rights:** original papers, licensed data and source PDFs are not redistributed here without license verification.


## Active chemical-identity and environmental-pathway verification (2026-10-13)

**Separate evidence dimensions, not a validated training cohort:**
- **17 proposed reference chemical structures** linked to public chemical identifiers; the identity/physical form/stereochemistry of actual toxicity test standards is **not independently confirmed**.
- **11 distinct route hypotheses** with original environmental formation or field-pathway references, or explicit negative/unresolved evidence flags.
- **19 unique provisional assay comparisons** in the reviewer queue: 6 earlier priority records, 9 additional nonduplicate Mount (2025) assay records, and 4 Xiong (2023) chemical pairs.
- **Three conditional Xiong molar ratios** can be computed from proposed neutral molecular structures; they are not approved scientific labels. M-acetaminophen remains chemically unresolved.
- **Zero independent reviewer approvals** and **no validated empirical parent-product prediction model**.

### Start here

- [Reference chemical identity registry](data/chemical_identity_reference_NOT_ASSAY_APPROVED.csv)
- [Environmental transformation pathway ledger](data/environmental_pathway_evidence_11_routes_UNAPPROVED.csv)
- [Independent toxicology review guide](review/INDEPENDENT_REVIEW_INSTRUCTIONS.md)
- [Blank route reviewer template](review/route_adjudication_TEMPLATE_BLANK.csv)
- [Blank observation reviewer template](review/observation_adjudication_TEMPLATE_BLANK.csv)
- [New toxicity-study recovery queue](data/independent_study_discovery_queue.csv)
- [Open evidence-adjudication issue](https://github.com/kiran978/TransHazard/issues/1)

Run reference-structure and route QA locally with:
```bash
python src/transhazard/identity_review.py --report outputs/identity_pathway_gate.json
python src/transhazard/evidence_audit.py --report outputs/expanded_evidence_audit.json
python -m unittest discover -s tests -v
```

**No raw publications, signed reviewer records or sensitive data are redistributed through the public repository.**
