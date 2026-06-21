# HHbtag training

[HHbtag](https://github.com/cms-flaf/HHbtag) is the HH-optimised b-jet identification used by the
analysis. This page covers the **specialised** workflow of producing the training skim — only
needed if you are (re)training the tagger, not for normal analysis runs.

## Produce the training skim

```sh
python Studies/HHBTag/CreateTrainingSkim.py \
  --inFile  <NANOAOD_INPUT>.root \
  --outFile output/skim.root \
  --mass 350 --sample GluGluToBulkGraviton --year 2018 >& EventInfo.txt
```

!!! note "Adapt the example to your inputs"
    The arguments above (`--mass`, `--sample`, `--year`, the input path) are an illustration. Point
    `--inFile` at the NanoAOD signal sample you want to train on and set `--mass`/`--sample`/`--year`
    accordingly. Check `CreateTrainingSkim.py --help` for the current options.

The skim is the input to the HHbtag training itself, which lives in the
[HHbtag repository](https://github.com/cms-flaf/HHbtag).

!!! tip "You usually don't need this"
    Standard analysis productions use the **already-trained** HHbtag model that ships with the
    `HHbtag` submodule. Retraining is an expert task done rarely.
