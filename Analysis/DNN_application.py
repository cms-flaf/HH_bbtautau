from __future__ import annotations
import os, sys
import numpy as np
import awkward as ak
import psutil
import yaml
import os
import ROOT
import FLAF.Common.Utilities as Utilities
import Analysis.hh_bbtautau as analysis
import tensorflow as tf
from Analysis.interface import NNInterface
import enum

class DNNProducer:
    def __init__(self, cfg, payload_name, period, global_params):

        self.payload_name = payload_name
        self.period = period
        self.cfg = global_params

        sys.path.append(os.environ["ANALYSIS_PATH"])
        ROOT.gROOT.ProcessLine(".include " + os.environ["ANALYSIS_PATH"])
        ROOT.gInterpreter.Declare(f'#include "FLAF/include/Utilities.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/HistHelper.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/AnalysisTools.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/AnalysisMath.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/MT2.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/Lester_mt2_bisect.cpp"')
        self.dnnConfig = cfg

        self.models = self.load_models(self.dnnConfig["model_dir"])
        self.features = self.dnnConfig["features"]

        self.cols_to_save = [
            f"{self.payload_name}_{col}" for col in self.dnnConfig["columns"]
        ]
        load_features = self.features
        self.vars_to_save = load_features
        

    def load_models(self, model_dir):
        models = [
            NNInterface(
                fold_index=fold_index,
                model_path=os.path.join(
                    model_dir,
                    f"model_fold{fold_index}_moe",
                ),
            )
            for fold_index in range(NNInterface.n_folds)
        ]
        return models
    
    def prepare_dfw(self, rdf, dataset):
        rdf.df = analysis.PrepareDfForDNN(analysis.DataFrameBuilderForHistograms(rdf.df, self.cfg, self.period)).df
        rdf.df = rdf.df.Define("entry_index", "(UInt_t)(FullEventId & 0xFFFFFFFF)")
        return rdf

    def run(self, array):
        array = self.ApplyDNN(array)

        # Delete not-needed branches
        for col in array.fields:
            if col not in self.dnnConfig["columns"]:
                if col != "FullEventId":
                    del array[col]

        # Rename the branches
        for col in self.dnnConfig["columns"]:
            if col in array.fields:
                array[f"{self.payload_name}_{col}"] = array[f"{col}"]
                del array[f"{col}"]
            else:
                print(f"Expected column {col} not found in your payload array!")

        return array

    def ApplyDNN(self, array):
        models = self.models
        
        other_columns_dict = array
        num_events = len(array["event"])

        if num_events == 0:
            print(f"No events found for {tree_name}, skipping inference.")
            return

        predictions_array = np.zeros(
            (NNInterface.n_folds, num_events, NNInterface.n_out)
        )
        for fold_index, nn_interface in enumerate(models):
            for i in range(num_events):
                if i % 10000 == 0:
                    print(f"  Event No. {i}")

                event_data = {col: array[col][i] for col in self.features}
                if event_data["channelId"] not in [13,23,33]:
                    continue
                inputs = convert_to_numpy(event_data, self.period, 400, 2)

                predictions = self.run_inference(nn_interface, inputs)
                predictions_array[fold_index, i, :] = predictions.flatten()

        mean_predictions = np.nanmean(predictions_array, axis=0)
        print(f"Mean predictions: {mean_predictions}")
        for i, col in enumerate(self.dnnConfig["columns"]):
            array[f"{col}"] = mean_predictions[:, i]
        
        return array
    
    def run_inference(self,nn_interface, inputs):
        predictions = nn_interface(**inputs)
        return predictions
    

def convert_to_numpy(event_data, period, mass, spin):
    dau1_px, dau1_py, dau1_pz, dau1_e = convert_kinematics(
        event_data["tau1_pt"],
        event_data["tau1_eta"],
        event_data["tau1_phi"],
        event_data["tau1_mass"],
    )
    dau2_px, dau2_py, dau2_pz, dau2_e = convert_kinematics(
        event_data["tau2_pt"],
        event_data["tau2_eta"],
        event_data["tau2_phi"],
        event_data["tau2_mass"],
    )
    bjet1_px, bjet1_py, bjet1_pz, bjet1_e = convert_kinematics(
        event_data["b1_pt"],
        event_data["b1_eta"],
        event_data["b1_phi"],
        event_data["b1_mass"],
    )
    bjet2_px, bjet2_py, bjet2_pz, bjet2_e = convert_kinematics(
        event_data["b2_pt"],
        event_data["b2_eta"],
        event_data["b2_phi"],
        event_data["b2_mass"],
    )

    selected_fatjet_pt = np.array(event_data["SelectedFatJet_pt"])
    selected_fatjet_eta = np.array(event_data["SelectedFatJet_eta"])
    selected_fatjet_phi = np.array(event_data["SelectedFatJet_phi"])
    selected_fatjet_mass = np.array(event_data["SelectedFatJet_mass"])

    if len(selected_fatjet_pt) != 0:
        max_pt_index = np.argmax(selected_fatjet_pt)
        fatjet_pt = selected_fatjet_pt[max_pt_index]
        fatjet_eta = selected_fatjet_eta[max_pt_index]
        fatjet_phi = selected_fatjet_phi[max_pt_index]
        fatjet_mass = selected_fatjet_mass[max_pt_index]
        fatjet_px, fatjet_py, fatjet_pz, fatjet_e = convert_kinematics(
            fatjet_pt, fatjet_eta, fatjet_phi, fatjet_mass
        )
    else:
        fatjet_px, fatjet_py, fatjet_pz, fatjet_e = 0.0, 0.0, 0.0, 0.0

    met_px, met_py, _, _ = convert_kinematics(
        event_data["met_pt"], 0, event_data["met_phi"], 0
    )

    def ai(v):
        return np.array([v], dtype=np.int32)

    def al(v):
        return np.array([v], dtype=np.int64)

    def af(v):
        return np.array([v], dtype=np.float32)

    pairtype_map = {23: 0, 13: 1, 33: 2}

    inputs = {
        "event_number": al(event_data["entry_index"]),
        "spin": ai(spin),
        "mass": ai(mass),
        "era": Era[period],
        "pair_type": ai(pairtype_map.get(event_data["channelId"], 2)),
        "dau1_dm": ai(event_data["tau1_decayMode"]),
        "dau2_dm": ai(event_data["tau2_decayMode"]),
        "dau1_charge": ai(event_data["tau1_charge"]),
        "dau2_charge": ai(event_data["tau2_charge"]),
        "is_boosted": ai(event_data["boosted_baseline"]),
        "has_bjet_pair": ai(event_data["Hbb_isValid"]),
        "met_px": af(met_px),
        "met_py": af(met_py),
        "met_cov00": af(event_data["met_covXX"]),
        "met_cov01": af(event_data["met_covXY"]),
        "met_cov11": af(event_data["met_covYY"]),
        "dau1_e": af(dau1_e),
        "dau1_px": af(dau1_px),
        "dau1_py": af(dau1_py),
        "dau1_pz": af(dau1_pz),
        "dau2_e": af(dau2_e),
        "dau2_px": af(dau2_px),
        "dau2_py": af(dau2_py),
        "dau2_pz": af(dau2_pz),
        "bjet1_e": af(bjet1_e),
        "bjet1_px": af(bjet1_px),
        "bjet1_py": af(bjet1_py),
        "bjet1_pz": af(bjet1_pz),
        "bjet1_btag_df": af(event_data["b1_btagDeepFlavB"]),
        "bjet1_cvsb": af(event_data["b1_btagPNetCvB"]),
        "bjet1_cvsl": af(event_data["b1_btagPNetCvL"]),
        "bjet1_hhbtag": af(event_data["b1_HHbtag"]),
        "bjet2_e": af(bjet2_e),
        "bjet2_px": af(bjet2_px),
        "bjet2_py": af(bjet2_py),
        "bjet2_pz": af(bjet2_pz),
        "bjet2_btag_df": af(event_data["b2_btagDeepFlavB"]),
        "bjet2_cvsb": af(event_data["b2_btagPNetCvB"]),
        "bjet2_cvsl": af(event_data["b2_btagPNetCvL"]),
        "bjet2_hhbtag": af(event_data["b2_HHbtag"]),
        "fatjet_e": af(np.array(fatjet_e)),
        "fatjet_px": af(np.array(fatjet_px)),
        "fatjet_py": af(np.array(fatjet_py)),
        "fatjet_pz": af(np.array(fatjet_pz)),
    }
    return inputs

def convert_kinematics(pt, eta, phi, mass):
    px = pt * np.cos(phi)
    py = pt * np.sin(phi)
    pz = pt * np.sinh(eta)
    energy = np.sqrt(pt**2 * np.cosh(eta) ** 2 + mass**2)
    return px, py, pz, energy

class Era(enum.Enum):

    Run2_2016H = 1
    Run2_2016 = 2
    Run2_2017 = 3
    Run2_2018 = 4
    Run3_2022 = 5
    Run3_2022EE = 6
    Run3_2023 = 7
    Run3_2023BPix = 8
    Run3_2024 = 9
    Run3_2025 = 10