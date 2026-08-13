# HH → bb̄ττ

This is the documentation for the **HH→bb̄ττ** analysis — the search for Higgs-boson pair
production in the bb̄ττ final state. It is the **reference analysis** of the
[FLAF framework](https://cms-flaf.github.io/FLAF/) and the most feature-complete.

!!! abstract "The common workflow lives in the FLAF docs"
    HH→bb̄ττ runs on FLAF, so the installation model, the task pipeline (NanoAOD → anaTuples →
    histograms → plots), the configuration system, storage, eras and CI are **the same as for every
    FLAF analysis** and are documented once, in the **[FLAF documentation](https://cms-flaf.github.io/FLAF/)**:

    - [Prerequisites & installation](https://cms-flaf.github.io/FLAF/getting-started/installation/)
    - [Your first run](https://cms-flaf.github.io/FLAF/getting-started/first-run/)
    - [Full workflow walkthrough](https://cms-flaf.github.io/FLAF/workflow/walkthrough/)
    - [Command arguments](https://cms-flaf.github.io/FLAF/workflow/arguments/)

    **This site covers only what is specific to HH→bb̄ττ.**

## What this analysis adds on top of FLAF

| Ingredient | Purpose |
|---|---|
| **SVfit** (`ClassicSVfit`, `SVfitTF`) | Reconstruct the di-τ system mass. |
| **HHKinFit2** | Kinematic fit of the HH system. |
| **HHbtag** | HH-optimised b-jet identification. |
| **DeepTau** | τ identification; the version is selectable (`2p1`/`2p5`). |
| Resonant + non-resonant signals | Radion (spin-0) & Bulk Graviton (spin-2); ggF & VBF non-resonant. |
| **StatInference** | Datacards, resonant & non-resonant limits, pulls & impacts. |

The setup of these pieces is in [Setup](setup.md); how they enter a run is in
[Running the analysis](analysis.md); the statistics step is in
[Statistical inference](stat_inference.md).

## Quickstart

```sh
git clone --recursive git@github.com:cms-flaf/HH_bbtautau.git
cd HH_bbtautau
source env.sh                                  # first time builds the environment
voms-proxy-init -voms cms -rfc -valid 192:00
law index --verbose
```

Then smoke-test the whole chain (see
[FLAF → first run](https://cms-flaf.github.io/FLAF/getting-started/first-run/)):

```sh
law run FLAF.Analysis.tasks.HistPlotTask \
  --version my_first_run --period Run3_2022 --workflow local --branches 0 --test 1000
```

New to FLAF? Read [Key terms](https://cms-flaf.github.io/FLAF/getting-started/key-terms/) and the
[Concepts](https://cms-flaf.github.io/FLAF/concepts/architecture/) section first.

## Eras

HH→bb̄ττ currently runs over the Run 3 eras `Run3_2022`, `Run3_2022EE`, `Run3_2023`,
`Run3_2023BPix`, `Run3_2024`, `Run3_2025` and `Run3_2026`. 2025 and 2026 reuse the
2024 Summer24 MC (with that year's corrections); see
[FLAF → Eras](https://cms-flaf.github.io/FLAF/concepts/eras/).
