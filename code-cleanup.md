# Code Clean-Up
### [**HH_bbtautau/config/global.yaml**](https://github.com/cms-flaf/HH_bbtautau/blob/96436eaf97a191bfde2f935d03cd1cdee69e77a2/config/global.yaml)

```yaml
https://github.com/cms-flaf/HH_bbtautau/blob/96436eaf97a191bfde2f935d03cd1cdee69e77a2/config/global.yaml#L6-L11

signal_types:
  - HHnonRes # We are now doing the Non-resonant study.
  # - GluGluToRadion
  # - GluGluToBulkGraviton
  # - VBFToRadion
  # - VBFToBulkGraviton
```

```yaml
corrections:
  lumi: { stage: AnaTuple }
  xs: { stage: AnaTuple }
  gen: { stage: AnaTuple }
  pu:
    stages: [ AnaTuple, AnaTupleMerge ]
    enabled:
      AnaTuple: true
      AnaTupleMerge: false
  base: { stage: AnaTupleMerge }
  tauID: { stage: HistTuple }
  tauES: { stage: AnaTuple }
  mu:
    stage: HistTuple
    columns:
      pfRelIso04_all: Muon_pfRelIso04_all
      tightId: Muon_tightId
      tkRelIso: Muon_tkRelIso
      highPtId: Muon_highPtId
      mediumId: Muon_mediumId
      looseId: Muon_looseId
  trigger:
    stage: HistTuple
    mode: efficiency
  ele: { stage: HistTuple }
  muScaRe: { stage: AnaTuple, mu_pt_for_ScaReApplication: "nano" }
  eleES: { stage: AnaTuple }
  JEC: { stage: AnaTuple }
  JER:
    stage: AnaTuple
    apply_jet_horns_fix: true
  btag:
    stages: [ AnaTuple ]
    modes:
      AnaTuple: shape
    tagger: particleNet
    jetCollection: centralJet

extraFormat_for_triggerMatchingAndSF:
  pt: "nano"
muon_pt_for_presel: "nano"
mu_pt_for_triggerMatchingAndSF: "nano"
mu_pt_for_selection: "pt"
mu_pt_for_definitions: "ScaRe" # here options are different: corr, nano, bsConstrainedPt, roccor
muonID_WP_for_triggerSF: "Tight" # only medium or tight for trigger SF, both iso and ID
muIDWP: "Tight"
muIsoWP: "Tight"
  
  
 # need to apply any MET correction ? Jet and Tau coorection to MET
 check this extraFormat 
 we are missing recoil, DY Correction, 
```

```yaml
triggers:
  eTau: [ singleEle, etau]
  muTau: [singleMu, mutau]
  tauTau: [ditau]
  eE: [singleEle]
  eMu: [singleEle, singleMu]
  muMu: [singleMu]

hist_triggers:
  eTau:
    default: ( ( (HLT_singleEle || HLT_etau ) && Legacy_region ) || (HLT_singleTau && SingleTau_region && !Legacy_region)  || (HLT_MET && (!(Legacy_region) && !(SingleTau_region)) ))
    ~~Run2_2016 :  ( ( (HLT_singleEle && SingleEle_region) || (HLT_singleTau && SingleTau_region && !Legacy_region) || (HLT_MET && (!(Legacy_region) && !(SingleTau_region)) )))
    Run2_2016_HIPM :  ( ( (HLT_singleEle && SingleEle_region) || (HLT_singleTau && SingleTau_region && !Legacy_region) || (HLT_MET && (!(Legacy_region) && !(SingleTau_region)) )))~~
  muTau:
    default: (( (HLT_singleMu || HLT_mutau ) && Legacy_region ) || (HLT_singleTau && SingleTau_region && !Legacy_region)  || (HLT_MET && (!(Legacy_region) && !(SingleTau_region)) ))
  tauTau:
    default: ((HLT_ditau && Legacy_region) || (HLT_singleTau && SingleTau_region && !Legacy_region)  || (HLT_MET && (!(Legacy_region) && !(SingleTau_region)) ) )
  eE:
    default: (HLT_singleEle && SingleEle_region)
  eMu:
    default: ((HLT_singleEle && SingleEle_region) || (HLT_singleMu && SingleMu_region))
  muMu:
    default: (HLT_singleMu && SingleMu_region)
```

```yaml
 # Right now we need only 5: baseline, inclusive, res1b, res2b and boosted - the rest should be removed
 
region: SR
region_default: SR
custom_regions: QCDRegions
custom_categories: ""
custom_subcategories: [ ]

QCDRegions:
  - OS_Iso
  - SS_Iso
  - OS_AntiIso
  - SS_AntiIso

boosted_categories:
  # - boosted_cat2
  # - boosted_cat3
  # - boosted_masswindow
  # - boosted_cat2_masswindow
  - boosted_cat3_masswindow
  
categories:
  - inclusive
  ~~ - btag_shape ~~
  - baseline
  - boosted_baseline
  # - boosted_baseline_cat3
  # - boosted_baseline_masswindow
  # - boosted_baseline_cat3_masswindow
  - res0b_inclusive
  - res1b_inclusive
  - res2b_inclusive
  - boosted
  # - boosted_cat3
  # - res0b_cat2
  # - res1b_cat2
  # - res2b_cat2
  # - res2b_cat3
  # - res1b_cat3
  # - res0b_cat3
  # - inclusive_masswindow
  # - btag_shape_masswindow
  # - baseline_masswindow
  # - res0b_inclusive_masswindow
  # - res1b_inclusive_masswindow
  # - res2b_inclusive_masswindow
  # - res0b_cat2_masswindow
  # - res1b_cat2_masswindow
  # - res2b_cat2_masswindow
  # - res2b_cat3_masswindow
  # - res1b_cat3_masswindow
  # - res0b_cat3_masswindow
 
 we need to have the VBF category, VBF inclusive, basic one. 
 
category_definition:
  # w/o mass window

  # boosted_baseline: "(SelectedFatJet_p4[fatJet_sel].size()>0)"
  inclusive: "b2_pt>0"  # "!(boosted_baseline)"
  btag_shape: "!(boosted_baseline)"
  baseline: "return true;"
  res0b_inclusive: "nSelBtag == 0"
  res1b_inclusive: "nSelBtag == 1"
  res2b_inclusive: "nSelBtag == 2"
  boosted: "SelectedFatJet_p4[fatJet_sel && SelectedFatJet_particleNet_MD_JetTagger>={pNetWP}].size()>0"
  res0b_cat2: "!boosted_baseline && nSelBtag == 0 "
  res1b_cat2: "!boosted_baseline && nSelBtag == 1 "
  res2b_cat2: "!boosted_baseline && nSelBtag == 2 "
  boosted_cat2: "SelectedFatJet_p4[fatJet_sel && SelectedFatJet_particleNet_MD_JetTagger>={pNetWP}].size()>0 "
  res2b_cat3: "nSelBtag == 2"
  boosted_baseline_cat3: "!(res2b_cat3) && (boosted_baseline)"
  boosted_cat3: "!(res2b_cat3) && boosted"  # (SelectedFatJet_p4[fatJet_sel && SelectedFatJet_particleNet_MD_JetTagger>={pNetWP}].size()>0) && {region}_boosted"
  res1b_cat3: "!(res2b_cat3) && !(boosted_baseline_cat3) && nSelBtag == 1"
  res0b_cat3: "!(res2b_cat3) && !(boosted_baseline_cat3) && nSelBtag == 0"

  # w/ mass window
  # boosted_baseline: "(SelectedFatJet_p4[fatJet_sel].size()>0)" (commenting this out because it has been defined under w/o mass window already)
  inclusive_masswindow: "!(boosted_baseline) && {region}"
  btag_shape_masswindow: "!(boosted_baseline) && {region}"
  baseline_masswindow: "return {region};"
  res0b_inclusive_masswindow: "nSelBtag == 0 && {region}"
  res1b_inclusive_masswindow: "nSelBtag == 1 && {region}"
  res2b_inclusive_masswindow: "nSelBtag == 2 && {region}"

  boosted_baseline_masswindow: "(SelectedFatJet_p4[fatJet_sel].size()>0) && {region}_boosted"
  boosted_masswindow: "SelectedFatJet_p4[fatJet_sel && SelectedFatJet_particleNet_MD_JetTagger>={pNetWP}].size()>0 && {region}_boosted"
  res0b_cat2_masswindow: "!boosted_baseline && nSelBtag == 0 && {region}"
  res1b_cat2_masswindow: "!boosted_baseline && nSelBtag == 1 && {region}"
  res2b_cat2_masswindow: "!boosted_baseline && nSelBtag == 2 && {region}"
  boosted_cat2_masswindow: "SelectedFatJet_p4[fatJet_sel && SelectedFatJet_particleNet_MD_JetTagger>={pNetWP}].size()>0 && {region}_boosted"

  res2b_cat3_masswindow: "nSelBtag == 2 && {region}"
  boosted_baseline_cat3_masswindow: "!(res2b_cat3_masswindow) && (boosted_baseline)"
  boosted_cat3_masswindow: "!(res2b_cat3_masswindow) && boosted_masswindow"  # (SelectedFatJet_p4[fatJet_sel && SelectedFatJet_particleNet_MD_JetTagger>={pNetWP}].size()>0) && {region}_boosted"
  res1b_cat3_masswindow: "!(res2b_cat3_masswindow) && !(boosted_baseline_cat3) && nSelBtag == 1 && {region}"
  res0b_cat3_masswindow: "!(res2b_cat3_masswindow) && !(boosted_baseline_cat3) && nSelBtag == 0 && {region}"

```

```yaml
check the trigger config, could be duplication

singleMu_th:
  "Run2_2016": 26
  "Run2_2016_HIPM": 26
  "Run2_2017": 29
  "Run2_2018": 26
  "Run3_2022": 26
  "Run3_2022EE": 26
  "Run3_2023": 26
  "Run3_2023BPix": 26

singleEle_th:
  "Run2_2016": 26
  "Run2_2016_HIPM": 26
  "Run2_2017": 33
  "Run2_2018": 33
  "Run3_2022": 32
  "Run3_2022EE": 32
  "Run3_2023": 32
  "Run3_2023BPix": 32

singleTau_th:
  "Run2_2016": 130
  "Run2_2016_HIPM": 130
  "Run2_2017": 190
  "Run2_2018": 190
  "Run3_2022": 190
  "Run3_2022EE": 190
  "Run3_2023": 190
  "Run3_2023BPix": 190

eTau_th:
  "Run2_2016":
  "Run2_2016_HIPM":
  "Run2_2017":
  "Run2_2018":
  "Run3_2022":
  "Run3_2022EE":
  "Run3_2023":
  "Run3_2023BPix":

muTau_th:
  "Run2_2016":
  "Run2_2016_HIPM":
  "Run2_2017":
  "Run2_2018":
  "Run3_2022":
  "Run3_2022EE":
  "Run3_2023":
  "Run3_2023BPix":

```

```yaml
Uncertatinties are in another PR.

# preVFP == APV == HIPM
unc_2018:
  - JES_BBEC1_2018
  - JES_Absolute_2018
  - JES_EC2_2018
  - JES_HF_2018
  - JES_RelativeSample_2018
unc_2017:
  - JES_BBEC1_2017
  - JES_Absolute_2017
  - JES_EC2_2017
  - JES_HF_2017
  - JES_RelativeSample_2017
unc_2016preVFP:
  - JES_BBEC1_2016preVFP
  - JES_Absolute_2016preVFP
  - JES_EC2_2016preVFP
  - JES_HF_2016preVFP
  - JES_RelativeSample_2016preVFP
unc_2016postVFP:
  - JES_BBEC1_2016postVFP
  - JES_Absolute_2016postVFP
  - JES_EC2_2016postVFP
  - JES_HF_2016postVFP
  - JES_RelativeSample_2016postVFP
  - JES_RelativeSample_2016postVFP
```

```yaml
uncs_to_exclude:
  Run3_2022: [ ]
  Run3_2022EE: [ ]
  Run3_2023: [ ]
  Run3_2023BPix: [ ]
  ~~Run2_2018:
    - JES_BBEC1_2017
    - JES_Absolute_2017
    - JES_EC2_2017
    - JES_HF_2017
    - JES_RelativeSample_2017
    - JES_BBEC1_2016preVFP
    - JES_Absolute_2016preVFP
    - JES_EC2_2016preVFP
    - JES_HF_2016preVFP
    - JES_RelativeSample_2016preVFP
    - JES_BBEC1_2016postVFP
    - JES_Absolute_2016postVFP
    - JES_EC2_2016postVFP
    - JES_HF_2016postVFP
    - JES_RelativeSample_2016postVFP
  Run2_2017:
    - JES_BBEC1_2018
    - JES_Ab~~solute_2018
    ~~- JES_EC2_2018
    - JES_HF_2018
    - JES_RelativeSample_2018
    - JES_BBEC1_2016preVFP
    - JES_Absolute_2016preVFP
    - JES_EC2_2016preVFP
    - JES_HF_2016preVFP
    - JES_RelativeSample_2016preVFP
    - JES_BBEC1_2016postVFP
    - JES_Absolute_2016postVFP
    - JES_EC2_2016postVFP
    - JES_HF_2016postVFP
    - JES_RelativeSample_2016postVFP
  Run2_2016:
    - JES_BBEC1_2018
    - JES_Absolute_2018
    - JES_EC2_2018
    - JES_HF_2018
    - JES_RelativeSample_2018
    - JES_BBEC1_2017
    - JES_Absolute_2017
    - JES_EC2_2017
    - JES_HF_2017
    - JES_RelativeSample_2017
    - JES_BBEC1_2016preVFP
    - JES_Absolute_2016preVFP
    - JES_EC2_2016preVFP
    - JES_HF_2016preVFP
    - JES_RelativeSample_2016preVFP
  Run2_2016_HIPM:
    - JES_BBEC1_2018
    - JES_Absolute_2018
    - JES_EC2_2018
    - JES_HF_2018
    - JES_RelativeSample_2018
    - JES_BBEC1_2017
    - JES_Absolute_2017
    - JES_EC2_2017
    - JES_HF_2017
    - JES_RelativeSample_2017
    - JES_BBEC1_2016postVFP
    - JES_Absolute_2016postVFP
    - JES_EC2_2016postVFP
    - JES_HF_2016postVFP
    - JES_RelativeSample_2016postVFP~~
```

**Analysis/hh_bbtautau.py**

```python
if __name__ == "__main__":
    sys.path.append(os.environ["ANALYSIS_PATH"])

~~if __name__ == "__main__":
    sys.path.append(os.environ["ANALYSIS_PATH"])
    sys.path.append(os.environ["ANALYSIS_PATH"])~~ 
    

 def defineLeptonPreselection(self):  # needs channel def
        ~~if self.period == "Run2_2016" or self.period == "Run2_2016_HIPM":
            self.df = self.df.Define(
                "eleEta2016",
                "if(eE) {return (abs(tau1_eta) < 2 && abs(tau2_eta)<2); } if(eTau||eMu) {return (abs(tau1_eta) < 2); } return true;",
            )
        else:
            self.df = self.df.Define("eleEta2016", "return true;")~~
        self.df = self.df.Define(
            "muon1_tightId",
            "if(muTau || muMu) {return (tau1_Muon_tightId && tau1_Muon_pfRelIso04_all < 0.15); } return true;",
        )
        self.df = self.df.Define(
            "muon2_tightId",
            "if(muMu || eMu) {return (tau2_Muon_tightId && tau2_Muon_pfRelIso04_all < 0.3);} return true;",
        )
        self.df = self.df.Define(
            "firstele_mvaIso",
            "if(eMu || eE){return tau1_Electron_mvaIso_WP80==1 && tau1_Electron_pfRelIso03_all < 0.15 ; } return true; ",
        )
        self.df = self.df.Define(
            "tau1_iso_medium",
            f"if(tauTau) return (tau1_idDeepTau{self.deepTauYear()}v{self.deepTauVersion}VSjet >= {Utilities.WorkingPointsTauVSjet.Medium.value}); return true;",
        )
        if f"tau1_gen_kind" not in self.df.GetColumnNames():
            self.df = self.df.Define("tau1_gen_kind", "if(isData) return 5; return 0;")
        if f"tau2_gen_kind" not in self.df.GetColumnNames():
            self.df = self.df.Define("tau2_gen_kind", "if(isData) return 5; return 0;")
        self.df = self.df.Define(
            "tau_true", f"""(tau1_gen_kind==5 && tau2_gen_kind==5)"""
        )
        self.df = self.df.Define(
            f"lepton_preselection",
            "~~eleEta2016~~ && tau1_iso_medium && muon1_tightId && muon2_tightId && firstele_mvaIso",
        )

```

Analysis/GetCrossWeights.py

```python
def defineTriggerWeightsErrors(dfBuilder):
	
	.
	.
	.
	
	~~if dfBuilder.period == "Run2_2016" or dfBuilder.period == "Run2_2016_HIPM":
	        dfBuilder.df = dfBuilder.df.Define(f"weight_trigSF_cross_mu_Up", " 1.f ")
	        dfBuilder.df = dfBuilder.df.Define(f"weight_trigSF_cross_mu_Down", " 1.f ")
	        dfBuilder.df = dfBuilder.df.Define(
	            f"weight_trigSF_SL_mu_Up",
	            "if ((HLT_singleMu) && Legacy_region ) {return weight_tau1_TrgSF_singleMuUp_rel*weight_tau1_TrgSF_singleMuCentral;} return 1.f; ",
	        )
	        dfBuilder.df = dfBuilder.df.Define(
	            f"weight_trigSF_SL_mu_Down",
	            "if ((HLT_singleMu) && Legacy_region ) {return weight_tau1_TrgSF_singleMuUp_rel*weight_tau1_TrgSF_singleMuCentral;} return 1.f; ",
	        )
	        dfBuilder.df = dfBuilder.df.Define(f"weight_trigSF_mu_Up", " 1.f; ")
	        dfBuilder.df = dfBuilder.df.Define(f"weight_trigSF_mu_Down", " 1.f; ")
	        dfBuilder.df = dfBuilder.df.Define(f"weight_trigSF_mutau_tau_Up", "  1.f; ")
	        dfBuilder.df = dfBuilder.df.Define(f"weight_trigSF_mutau_tau_Down", "  1.f; ")~~
```