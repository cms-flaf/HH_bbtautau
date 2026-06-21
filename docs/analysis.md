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
