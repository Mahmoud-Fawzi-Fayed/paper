# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This directory contains materials for revising the **FedFACS** paper — "FedFACS: A Fair Adaptive Client Selection Framework for Communication-Efficient Federated Learning" — submitted to the *Journal of King Saud University Computer and Information Sciences*. Both reviewers recommended rejection with substantial revision.

## Files

| File | Contents |
|------|----------|
| `original paper.pdf` | The originally submitted manuscript |
| `FedFACS_Reviewer_Comments_Verbatim.docx` | Full verbatim comments from Reviewer 1 (21 numbered concerns, R1-01–R1-21) and Reviewer 2 (23 numbered concerns, R2-01–R2-23) |
| `FedFACS_14_Before_After fixing comments.docx` | Revision companion: 14 specific before/after text replacements with cross-references to the reviewer concerns each replacement targets |
| `springer_submission/` (+ `springer_submission.zip`) | **Canonical revised manuscript**: `main.tex` (Springer Nature `sn-jnl` class, `sn-basic`), `sn-bibliography.bib`, `figs/`. Merges all 22 replacements. Not compiled (no TeX engine here); needs `sn-jnl.cls` and `sn-basic.bst` from the Springer Nature template (Overleaf). Red `\todo{}` markers are author-only fields (names, affiliations, funding, COI, contributions) |
| `FedFACS_14_Before_After_FINAL.docx` | **Current, concise paste-ready 14-replacement Before/After file** (After shortened ~30%, Declared box per replacement, highlighted Status/author actions, symbol renames J, Pi, X, Tx; main.tex updated to match). Previous: `..._COMPLETED.docx` (longer). Older description: (native Word equations): all 44 reviewer comments folded into the 14 replacements, per-replacement status T/P/O, coverage matrix and notation table. Supersedes `FedFACS_14_Before_After fixing comments.docx` |
| `FedFACS_Response_to_Reviewers_v2.docx` | **Current** point-by-point response (44 points: 22 addressed, 22 open), cites revised-manuscript sections |
| `FedFACS_Additional_Replacements_15-22.docx`, `FedFACS_Response_to_Reviewers.docx` | **Superseded** by the two entries above (contain inaccuracies, e.g. 25/19 count, garbled market-size note, notation claim); keep only for history |

## Working with DOCX Files

DOCX is a ZIP of XML. The workflow for editing:

```bash
# Unpack
cp file.docx file.zip && unzip -q file.zip -d unpacked/

# Merge fragmented runs so text is searchable (run before editing)
python scripts/merge_runs.py unpacked/

# Edit unpacked/word/document.xml in place — do NOT reformat or pretty-print

# Repack
(cd unpacked && rm -f ../out.docx && zip -XrD ../out.docx .)
```

The `scripts/` referenced above are in the docx skill's base directory. When adding tracked changes (redlines), wrap insertions in `<w:ins>` and deletions in `<w:del>`/`<w:delText>` with `w:id`, `w:author`, `w:date` attributes.

## Reviewer Comment Mapping Convention

The Before/After document uses this reference scheme:
- **R1-01–R1-21**: Reviewer 1's 21 substantive paragraphs in original order
- **R2-01–R2-23**: Reviewer 2's numbered concerns

## Core Technical Issues Requiring Resolution

The 14 replacements address these principal defects:

**Mathematical errors (must fix before resubmission):**
- **Eq. 7 (idle counter)**: Original rule never increments the counter for unselected clients — counter stays zero, breaking the entire fairness mechanism. Fix: unselected clients increment by 1; selected clients reset to 0.
- **Eq. 8 (control law)**: Denominator `λF + ν(ΔKL − F)` can be zero or negative. Fix: use `λF` (always positive since F ≥ 1) as denominator.
- **Eqs. 13/17–18 (aggregation weights)**: Raw stability scores `s = ΔKL − μσ²` can be negative, yielding negative aggregation weights. Fix: use positive-part normalization with sample-count fallback.
- **Eq. 16 (cohort size)**: Can produce non-integer values and values outside `[C_kmin, C_kmax]` when validation loss increases. Fix: add clamping and half-up rounding.

**Conceptual issues:**
- **Communication efficiency claim**: All N candidates download the model and train locally — only uploads are reduced. The original text claimed full communication savings. Fix: explicitly state that download, training, and scoring costs apply to all candidates.
- **Reference trajectory (Eq. 11)**: Original used a prior run of a competing baseline — unavailable in practice and circular. Fix: use a causal self-reference from prior FedFACS rounds with EMA smoothing (`β_ref = 0.9`).
- **KL utility interpretation**: ΔKL measures post-training divergence between local and global predictions, not a before/after reduction or evidence of improvement. Text must reflect this.

**Numerical inconsistencies to correct:**
- FMNIST Scenario 2 accuracy: 83.80% (not 83.08% as stated in one discussion location)
- Configuration B uses Pow-D (not FedProx) — baseline name must be consistent in text, tables, and figures
- FMNIST-S2 round reduction: 2.78% (not 2.2%)
- Table 4 F1/recall values for CIFAR-10 and FMNIST need reconciliation (F1 exceeds recall by 4–10 points, which is implausible for macro-averages)
- Table 5 COVID-19 average cohort (≈10.17) slightly exceeds the stated cap of m=10 — Configuration B bounds must be disclosed

## Status

Strict coverage of the 44 reviewer comments (Before/After FINAL, Appendix A): 24 resolved by text today (55%); 18 have corrected text with evidence in progress; 2 blocked on author inputs. Projected when the running experiments finish: 94% overall, every replacement >= 80% except Replacement 14 (62%), which needs the Zhai et al. and AHIBCS PDFs (Springer full texts not accessible). Nothing was fabricated.

**Experiments** live in `fedfacs_repro/` (v2 simulator: gradient clipping at 50 after a real NaN divergence at lr 0.05, failed-update exclusion, staged commit, confusion matrices). ONE sequential detached chain runs plan_main_a -> abl -> noise -> sens -> scale -> main_b (logs seq*.log; ~13-15 h); then plan_extra (FairFedCS, Greedy). Never run workers in parallel (GPU time-slicing made it slower). `python analyze.py` writes tables to `analysis/`. An hourly cron (session-only) monitors and restarts.

**Findings so far:** the method the manuscript calls "FedFairCS" is FairFedCS (arXiv 2307.10738); a 4-round pilot showed fixed vs controlled mixing identical (fairness term dominates, as Reviewer 2 argued); a 100-round pilot showed FedFACS ~10x download/compute for near-perfect participation fairness and ~equal accuracy.

**Authors still need to:** send Zhai et al. 2024 and AHIBCS PDFs; optionally provide the COVID-19 Kaggle data; confirm release statement; fill author/funding/COI fields; verify refs `mukhtiar2025b` and `huang2020`.
