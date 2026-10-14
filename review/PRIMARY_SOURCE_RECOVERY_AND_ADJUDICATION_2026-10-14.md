# Primary-source recovery and independent review — execution dossier

**Status as of 2026-10-14: NO Dataset v2 approval; no independently validated model.**

## Source 1 — Galaxolide (Li et al., 2026)
- Article DOI: https://doi.org/10.1039/D6EM00059B
- Publisher SI URL: https://www.rsc.org/suppdata/d6/em/d6em00059b/d6em00059b1.pdf
- Recovery state: SI link identified, PDF bytes and original matched 48-h LC50 rows not verified.
- Required: retrieve original SI, identify all HHCB and HHCB-lactone concentrations and fit estimates, verify exposure time, Daphnia species and life stage, analytical exposure basis, uncertainties and parent/product exact isomers, then verify phototransformation route under environmental conditions.
- **Do not interpret abstract LC50 ranges as matched point estimates.**

## Source 2 — Sulfoxaflor (2023)
- Article DOI: https://doi.org/10.1021/acs.jafc.2c08748
- Publisher supporting information: article's Supporting Information, Table S2 and Document S1 (as indexed in prior recovery register).
- Recovery state: SI numerical table not independently inspected; no original paired 24-h or 48-h LC50 accepted.
- Required: obtain publisher SI from authorized access or author, extract parent and each named metabolite's exact CAS/structure, endpoint/duration, censoring, uncertainty, solvent controls, concentration basis, and environmental transformation direction.
- **Do not substitute EFSA >-censored toxicity estimates for numerical endpoints or combine EFSA and 2023 study estimates.**

## Existing highest-priority identity/assay adjudications
1. Mount 2025: p,p-DDT→DDD mortality LC50; p,p-DDD→DDMU mortality LC50; DDE nonunique fit, o,p-DDT repeat variability, and DDMU biomass methanol control as separate HOLD decisions.
2. Kadlec 2024: 6:2 FTSA (acid vs salt) → PFHxA, 7-day Hyalella azteca biomass growth EC50; confirm analytical molecular-weight basis, life stage, curve fit and uncertainty.
3. Zhang 2011: malathion→malaoxon 24-h and 48-h Daphnia magna LC50, mixture stereochemistry, exposure conditions; retain corrected 48-h malaoxon value 2.08 ug/L as source-claimed pending verification.
4. Xiong 2023: methylparaben→4-hydroxybenzoic acid and naproxen→O-desmethylnaproxen; verify tested exact standards and whether environmental formation evidence applies to these identities.

## Formal review process
- One **route decision** and one **assay decision** per distinct unit, both ACCEPT/HOLD/EXCLUDE with a reasoned rationale and original primary-study evidence.
- At least one suitably qualified independent chemical-fate expert for pathway identity, and one aquatic ecotoxicology expert for assay comparability; institutional data steward authenticates the signoffs. A second reviewer or consensus process should resolve disagreements.
- Preserve signed records **privately**, not in the public GitHub repository. The repository stores only blank templates, deidentified decisions after permission, and auditable source pointers.
- No reviewer identities, signatures or approvals have been received. No software test, model output, or assistant analysis substitutes for their decisions.
- An observation can enter Dataset v2 only if **both** the route and assay are independently accepted, the exact test-standard identity is verified, release authorization is documented, and a reproducible freeze is created.

## Completion criteria
- [ ] Original publisher SI bytes obtained and their provenance/checksums documented for both studies.
- [ ] Original matched endpoints recovered or an explicit documented non-recoverable decision.
- [ ] All 11 existing routes and 19 observation records reviewed, with source-level justifications.
- [ ] New sources added only after independently verified chemical/assay/route matching.
- [ ] Reviewer decisions signed and release authorization authenticated.
- [ ] Dataset v2 release audit passes; independent external model validation follows only if data sufficiency permits.

**Important:** The existing review CSVs are deliberately blank. Do not pre-fill ACCEPT on behalf of experts.
