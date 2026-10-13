# Independent evidence adjudication: private review, public blank templates

This public repository contains **blank** route-level and observation-level assessment forms only. Do **not** commit signed reviews, personally identifying reviewer details, or copyrighted full-text PDFs to a public repository. Maintain signed documents in a controlled institutional record and publish only deidentified adjudication decisions/identifiers after authorization.

### Separate gates

- **Route identity and formation:** distinguish direct environmentally observed transformation, environmental field-inferred metabolite sequence, engineered water treatment oxidation, organism-only metabolism, and absent pathway data. Explicitly record multi-step chemistry and tested acid/salt/isomer identity.
- **Assay:** check species and life stage, duration, effect metric (LC50 vs EC50 vs biomass), exposure basis, censoring/limit dose, concentration-response quality, error type, experimental controls and primary source values.
- **Reviewer:** independent toxicology researcher or chemist records reasoned ACCEPT, HOLD or EXCLUDE; data steward separately authorizes release. Software only audits consistency. No automatic approval from a paper abstract, PubChem CAS, or positive CI bracket.
- **Model training:** requires complete approved release AND enough distinct disjoint network/publication groups per assay stratum. Current route and endpoint counts remain underpowered.

### Known urgent reviewer questions

1. Mount p,p'-DDE fitted LC50/biomass EC50 nonunique fit; DDMU biomass methanol control difference (p=0.004); o,p'-DDT two 7-day parent LC50s 1.40 and 0.60 µg/L; p,p'-DDD Test 1 did not yield LC50. Avoid counting repeat parent tests as independent reactions.
2. Kadlec 6:2 FTS vs PFHxA: parent salt/neutral acid reference, species life-stage record, fitted growth EC50, source confidence limits and exact measured concentration range. The formation path can be multistep.
3. Zhang malathion vs malaoxon: separate 24h and 48h; original 48h malaoxon LC50 2.08 µg/L vs erroneous imported 12.08; verify conditions and mixture stereochemistry.
4. Xiong acetaminophen methylated derivative identity cannot be assigned without the original chemical standards/SI; DO NOT infer O- versus N-methyl product. Diazepam to nordazepam observed organism metabolism, not demonstrated environmental demethylation.
5. Xiong methylparaben: candidate 4-hydroxybenzoic acid arises by **ester hydrolysis**, not simply an O-methyl ether demethylation; microbial direct formation in DOI 10.1128/AEM.67.6.2404-2409.2001. Verify Xiong original standard.
6. Xiong naproxen: a wastewater consortium produces O-desmethylnaproxen in DOI 10.1007/s00248-017-1136-2. Verify racemate vs (S)-enantiomer in actual tested standard.
7. DDT p,p field inferred paths do not validate the corresponding **o,p** isomer transformation without separate evidence.

### References (research pointers; do not mistake for approvals)
- Mount 2025 DOI 10.1093/etojnl/vgae070 and original 37-page Supplement S3.
- Xiong 2023 DOI 10.1021/acs.est.3c03242.
- 6:2 FTS in aerobic sludge DOI 10.1016/j.chemosphere.2010.11.003, sediment https://www.sciencedirect.com/science/article/pii/S0045653516303770
- DDT field chemistry DOI 10.1016/j.envpol.2017.12.071 and 10.1021/es7029619.
- Malathion aqueous oxidation DOI 10.1016/j.chemosphere.2019.06.058 and 10.1016/j.cej.2019.123793.

**Data status: 19 assay comparisons on this combined review queue, 11 route hypotheses, 17 reference chemical IDs. ZERO approved labels.**
