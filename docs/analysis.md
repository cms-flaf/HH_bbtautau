# Running the analysis

The pipeline itself — producing anaTuples, computing observables, filling and merging histograms,
plotting — is the **standard FLAF chain**. Follow the
**[FLAF full-workflow walkthrough](https://cms-flaf.github.io/FLAF/workflow/walkthrough/)** for the
commands (`InputFileTask` → `AnaTupleFileTask` → `AnaTupleMergeTask` → `HistTupleProducerTask` →
`HistFromNtupleProducerTask` → `HistMergerTask` → `HistPlotTask`). This page collects the points
that are **specific to HH→bb̄ττ**.

## Always pick the DeepTau version

Every stage that depends on τ identification must agree on the DeepTau version. Pass it
consistently across the whole production:

```sh
ERA=Run3_2022
VER=v1_deepTau2p5            # version name encodes the DeepTau version (see Setup)

law run FLAF.Analysis.tasks.HistPlotTask \
  --period $ERA --version $VER --workflow local \
  --customisations deepTauVersion=2p5
```

If you omit `deepTauVersion`, the default (`2p1`) is used. Keep the `--version` name and the
`deepTauVersion` customisation in sync to avoid mixing productions.

## Channels

HH→bb̄ττ is analysed in the three τ-pair channels — **eτ**, **μτ** and **ττ**. Channel selection is
driven by the analysis configuration (`config/global.yaml`); restrict or extend the channels there
or via your [`user_custom.yaml`](https://cms-flaf.github.io/FLAF/configuration/user-custom/).

## Choosing which variables to histogram

The set of variables produced by `HistFromNtupleProducerTask`/`HistPlotTask` is controlled by the
`variables:` list in your `user_custom.yaml` (or the `--variables` argument):

```yaml
variables:
  - tau1_pt
  - ggF_DNN_HH
```

Some observables are **computed in the cache step** (`AnalysisCacheTask`, e.g. the
LegacyVariables/heavier quantities) rather than directly from the anaTuple. When you request such a
variable, LAW pulls in the cache task automatically — see
[FLAF → Task reference](https://cms-flaf.github.io/FLAF/reference/tasks/#analysiscachetask). Listing
a short `variables:` set is the easiest way to keep test runs fast.

## Stitched backgrounds: DY

DY is stitched from several samples, so each event is normalised with the
cross-section of the bin it belongs to
([MC stitching](https://cms-flaf.github.io/FLAF/concepts/stitching/)). The bins select on
gen-level quantities that nanoAOD does not provide directly, so the anaTuple stores them:

| Branch | Stored for | Meaning |
|---|---|---|
| `DYInfo_flavor`, `DYInfo_mll` | `DYto2Tau_M_50` | flavour (11/13/15) and mass of the LHE dilepton pair |
| `TauTauInfo_passFilter` | `DYto2Tau_M_50` | the Z→ττ generator filter decision, the axis that stitches the filtered samples in |
| `TauTauInfo_vis_type{1,2}`, `TauTauInfo_vis_pt{1,2}`, `TauTauInfo_vis_abseta{1,2}` | `DYto2Tau_M_50` | the visible tau quantities the filter is made of, so its definition can be revisited without reprocessing |
| `TTInfo_nLeptonicW`, `TTInfo_wDecay{1,2}` | `TT` | gen-level t̄t decay channel |
| `genTop_{pt,eta,phi,mass}` | `TT` | last-copy top and anti-top, in this order; read by the top-p<sub>T</sub> reweighting |
| `genTop_b_{pt,eta,phi}`, `genTop_lep_{pt,eta,phi,mass}`, `genTop_lep_gen_kind` | `TT` | the b quark and the W's charged lepton of each top, and that lepton's `GenLepton::Kind` (-1 for a hadronic W) |

Which of these a process gets is declared as `genInfo` next to its `processors` in
`config/<era>/processes.yaml`, where a stitcher selects on it or, for `TT`, where the
top-p<sub>T</sub> reweighting reads `genTop_pt` (every era) — adding a kind to a process that is
already produced means producing it again; `AnaProd/genProcessInfo.py` turns that into the
branches above. The `genTop_*` arrays are defined before the event selection
(`defineGenVariables` in `AnaProd/anaTupleDef.py`), because the reweighting is a shape weight whose
denominator sums over all events. `TTInfo_*` columns must stay scalars: the anaTuple stores all
columns that share a prefix as one collection. A process that stitches on one of these quantities without declaring `genInfo` fails
in `AnaTupleMergeTask`, where `GenPart`/`LHEPart` are no longer available.

t̄t is not stitched: `TT` takes only the three decay-channel samples (`TTto2L2Nu`, `TTtoLNu2Q`,
`TTto4Q`) in every era, which do not overlap. The inclusive `TT`/`TT_ext1` samples of Run3_2022 and
Run3_2023BPix are not used: they carry no parton-shower weights (`PSWeight` has a single entry), on
which the parton-shower weight producer stops.

The integration test guards this. `TestModel` runs two backgrounds — `custom_CI_Background_TT`,
one t̄t dataset, and `custom_CI_Background_DY`, one DY→ττ dataset — and each carries the same
`processors:` and `genInfo:` as the real `TT` and `DYto2Tau_M_50` process **for that era**
(`DYtautauStitcher` for 2022–2023BPix, the plain `MCStitcher` for 2024 onwards, which is what
those eras configure). The stitchers therefore
run over the whole anaTuple → merge → histogram chain in CI, which is exactly where a missing
gen-level branch shows up. Change one of the real processes and change its CI counterpart with
it.

## Theory weights stored in the anaTuple

All MC is produced with the parton-shower ISR/FSR (`PSWeight`), PDF (`LHEPdfWeight`, 103 members)
and QCD-scale (`LHEScaleWeight`) weights, and t̄t with the top-p<sub>T</sub> reweighting
(`genTop_pt`, `data_nlo`). Each is a shape weight staged like the pileup weight: computed at
`AnaTupleFileTask`, where its inclusive sum enters the denominators, and turned into
`weight_base_<variation>_rel` at `AnaTupleMergeTask`. The merged anaTuple keeps `weight_base` and the
`weight_base_*_rel` branches and drops the per-member weights (`anaTupleMerge_drop_columns` in
`config/global.yaml`). They are not used in `weights.yaml` or the datacards yet; adding them there
needs no new anaTuple production.

`config/Run3_2024/global.yaml` (and 2025, 2026) inherits the analysis-wide `corrections:` block
through the anchor `*corrections_default` and overrides only `btag` (UParTAK4, no shape
calibration) and `dy_hhbbtautau`, so these weights, and any correction added to
`config/global.yaml`, apply to those eras too.

## Columns taken from the central tree

`config/global.yaml` lists in `anaTuple_shift_invariant_columns` the anaTuple columns that no
systematic shift changes: event numbers and dataset metadata, generator, luminosity and
cross-section weights, the pileup and theory weights, pileup truth, the LHE record, gen jets, the
stitching information (`DYInfo_*`, `TauTauInfo_*`, `TTInfo_*`), `genTop_*` and the gen-level signal
leptons (`genLepton{1,2}_*`). FLAF stores them in
the central tree only and fills them in for events that only a shift (JES, JER, tau or lepton
energy scale) selected, after checking that every variation agrees, so such events enter the
shifted templates with their real `weight_base` instead of 0.

- Only event-level generator quantities belong there. Generator information attached to a
  reconstructed object — `tau*_gen_*`, jet flavour labels, `nJetFromGenHbb` — follows the selected
  object and changes under the shifts; the fuse step stops with
  `Column '…' is declared shift-invariant but differs in …` if one is listed.
- Every input of `weight_base` (generator, luminosity, cross-section and shape weights, the
  stitching variables) must be listed, or an event selected only by a shift gets weight 0 there.
- A shifted tree reaches these columns through its `Central` friend, which `HasColumn` sees and
  `GetColumnNames()` does not list. A column that code downstream looks up with
  `GetColumnNames()` must stay off the list: the generator boson of the bosonic recoil correction
  (`recoil_GenBoson_*`) is invariant but is not listed for that reason.
- Changing the list changes the anaTuple layout, so it goes with a new anaTuple production.

### Signal points with more than one sample

Some GluGlutoHH points are produced more than once — an `_ext1` extension, or a variant
carrying LHE weights. Both are declared and both are used, so the point gets all the
statistics; the `GluGlutoHHto2B2Tau` process therefore carries the `*ext_processors`
stitcher, which normalises the point with the summed event count instead of counting it
twice ([MC stitching](https://cms-flaf.github.io/FLAF/concepts/stitching/)). Which samples
exist differs per era — Run3_2022EE, for instance, has only the LHE-weighted variant of
kl = 2.45 and no plain one.

## Quick stack plots

For a fast look at distributions (outside the full `HistPlotTask` styling), the analysis ships a
helper script. Edit the paths/variable names at the top to match your run, then:

```sh
cd Analysis
python3 make_stackplots.py
```

## Publishing plots

To share plots through a personal interactive web browser, see
[Interactive plot browser](interactive_plot_browser.md).

## Statistical interpretation

Once histograms exist, continue to [Statistical inference](stat_inference.md) for datacards,
limits and diagnostics.
