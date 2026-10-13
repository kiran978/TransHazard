# Li 2026 / Yuan 2023 Supplement Recovery — 2026-10-13

**Scope:** Recovery of publisher-listed original supplementary numerical toxicity tables, separate from source-index evidence and regulatory documents.

## Attempt 1: RSC Li et al. (2026), DOI 10.1039/D6EM00059B

- [Original journal article](https://pubs.rsc.org/en/content/articlelanding/2026/em/d6em00059b), which lists a 221 KB supporting information PDF.
- [Publisher-linked supplement URL](https://www.rsc.org/suppdata/d6/em/d6em00059b/d6em00059b1.pdf): direct file fetch timed out with the research browser; independent GitHub runner returned **HTTP 404**.
- Alternate journal supplementary route: **HTTP 403**.
- **Actual PDF contents not read**. Article abstract's two ranges cannot be treated as source-verified LC50 point estimates, 95% intervals, or paired ratios.

## Attempt 2: ACS Yuan et al. (2023), DOI 10.1021/acs.jafc.2c08748

- [Original journal article and its Supporting Information section](https://pubs.acs.org/doi/10.1021/acs.jafc.2c08748).
- Publisher index identifies `jf2c08748_si_001.pdf`, including **Table S2** for acute LC50s, **Figure S1** for dose response and **Document S1** for synthesized metabolite structures/purity.
- Conventional supplementary URL tested: **HTTP 403** (no PDF obtained).
- Alternative ACS Figshare DOI route tested: **HTTP 404** (no PDF obtained).
- **Actual PDF contents not read**; no 2023 LC50 numbers inferred from qualitative abstract claims.

## Confirmed independent source: EFSA regulatory assessment

- https://doi.org/10.2903/j.efsa.2014.3692 , 2014 opinion revised March 2015.
- Environmental fate pages 13–14: sulfoxaflor forms both **X11719474** and **X11519540** in dark aerobic soil; X11719474 also forms in sediment–water.
- Appendix A (printed p.144): acute 48h Daphnia LC50 **X11719474 >205000 µg/L** and **X11519540 >350000 µg/L**. These are **censored bounds**, derived from another set of experiments, not the Yuan et al. 2023 study's estimates. Source chemical form/isomers need independent verification before cross-study interpretation.

## Genuine outcome

**Three route hypotheses are prepared for actual independent review. No new exact paired toxicity-change label has been derived.** No independent researcher has returned a signed ACCEPT decision. Dataset v2 remains **NO-GO**. CI checks passed for anti-fabrication and censored-record gate invariants.

Recovery runner: https://github.com/kiran978/TransHazard/actions/runs/38383458266

Next handoff: an authorized researcher can access the two PDFs through the publisher's interactive SI links and supply them securely to the project; then source-level numerical extraction/fit/assay-standard review can continue.
