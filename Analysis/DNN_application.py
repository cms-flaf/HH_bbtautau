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
from interface import *

class DNNproducer:
    def __init__(self, cfg, payload_name, period):

        self.cfg = cfg
        self.payload_name = payload_name
        self.period = period

        sys.path.append(os.environ["ANALYSIS_PATH"])
        ROOT.gROOT.ProcessLine(".include " + os.environ["ANALYSIS_PATH"])
        ROOT.gInterpreter.Declare(f'#include "FLAF/include/Utilities.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/HistHelper.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/AnalysisTools.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/AnalysisMath.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/MT2.h"')
        ROOT.gROOT.ProcessLine(f'#include "FLAF/include/Lester_mt2_bisect.cpp"')

        self.dnnConfig = config["payload_producers"][payload_name]

        self.models = load_models(self.dnnConfig["model_dir"])
        self.features = self.dnnConfig["features"]

        self.cols_to_save = [
            f"{self.payload_name}_{col}" for col in self.cfg["columns"]
        ]
        load_features = self.features + ["event", "channelId", "FullEventId"]
        load_features = [col for col in load_features if col != "entry_index"]
        self.vars_to_save = load_features
        

    def load_models(model_dir):
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
    
    def Prepare_dfw(rdf, globalConfig, period):
        rdf_setup = analysis.PrepareDfForDNN(
            analysis.DataFrameBuilderForHistograms(rdf, globalConfig, period)
        ).df
        rdf_setup = rdf_setup.Define("entry_index", "(UInt_t)(FullEventId & 0xFFFFFFFF)")
        return rdf_setup

    def run(self, array):
        print("Running DNN producer")

        array = self.ApplyDNN(array)

        # Delete not-needed branches
        for col in array.fields:
            if col not in self.cfg["columns"]:
                if col != "FullEventId":
                    del array[col]

        # Rename the branches
        for col in self.cfg["columns"]:
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
            print(f"Processing Fold {fold_index} for {tree_name}")
            for i in range(num_events):
                if i % 100 == 0:
                    print(f"  Event No. {i}")

                event_data = {col: array[col][i] for col in self.features}
                if event_data["channelId"] not in [13,23,33]:
                    continue
                inputs = convert_to_numpy(event_data, period, mass, spin)

                predictions = run_inference(nn_interface, inputs)
                predictions_array[fold_index, i, :] = predictions.flatten()

        mean_predictions = np.nanmean(predictions_array, axis=0)
        for i, col in enumerate(self.columns):
            array[f"{col}"] = mean_predictions[:, i]
        
        return array
    
    def run_inference(nn_interface, inputs):
        predictions = nn_interface(**inputs)
        return predictions