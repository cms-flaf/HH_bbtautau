import os

from FLAF.Common.Utilities import DeclareHeader


# Gen-level information the MC stitching selects on. It is derived from GenPart/LHEPart,
# which the anaTuple does not keep, so it has to be stored here: the merge stage evaluates
# the same bin selections to pick the cross-section and the denominator, and can only read
# these back from the anaTuple. Which kinds a process needs is declared as `genInfo` in
# config/<era>/processes.yaml, next to the stitching processor that consumes them.
def addGenProcessInfo(dfw, gen_info):
    if "DY" in gen_info or "TauTau" in gen_info:
        DeclareHeader(
            os.path.join(os.environ["FLAF_PATH"], "include", "GenProcess", "DY.h")
        )
    if "TT" in gen_info:
        DeclareHeader(
            os.path.join(os.environ["FLAF_PATH"], "include", "GenProcess", "TT.h")
        )

    if "DY" in gen_info:
        dfw.Define(
            "_DYInfo",
            "gen_process::dy::identifyLHE(LHEPart_pt, LHEPart_eta, LHEPart_phi, "
            "LHEPart_mass, LHEPart_pdgId, LHEPart_status)",
        )
        dfw.DefineAndAppend("DYInfo_flavor", "_DYInfo.flavor")
        dfw.DefineAndAppend("DYInfo_mll", "_DYInfo.mll")

    if "TauTau" in gen_info:
        dfw.Define(
            "_TauTauInfo",
            "gen_process::dy::identifyTauTau(GenPart_pt, GenPart_eta, GenPart_phi, "
            "GenPart_mass, GenPart_pdgId, GenPart_statusFlags, "
            "GenPart_genPartIdxMother)",
        )
        dfw.DefineAndAppend("TauTauInfo_passFilter", "_TauTauInfo.passFilter()")
        # The quantities the filter is made of, so that a change of its definition does not
        # require reprocessing the nanoAOD again.
        for idx in range(2):
            dfw.DefineAndAppend(
                f"TauTauInfo_vis_type{idx + 1}",
                f"static_cast<int>(_TauTauInfo.vis_type[{idx}])",
            )
            dfw.DefineAndAppend(
                f"TauTauInfo_vis_pt{idx + 1}",
                f"static_cast<float>(_TauTauInfo.vis_pt[{idx}])",
            )
            dfw.DefineAndAppend(
                f"TauTauInfo_vis_abseta{idx + 1}",
                f"static_cast<float>(_TauTauInfo.vis_abseta[{idx}])",
            )

    if "TT" in gen_info:
        dfw.Define(
            "_TTInfo",
            "gen_process::tt::identify(GenPart_pdgId, GenPart_statusFlags, "
            "GenPart_genPartIdxMother)",
        )
        dfw.DefineAndAppend("TTInfo_nLeptonicW", "_TTInfo.nLeptonicW()")
        for idx in range(2):
            dfw.DefineAndAppend(
                f"TTInfo_wDecay{idx + 1}",
                f"static_cast<int>(_TTInfo.w_decay[{idx}])",
            )


# Generator-level t#bar{t} kinematics: a genTop collection ordered {top, anti-top} with the
# last-copy top, its b quark and its W's charged lepton (pt/eta/phi/mass, no b mass), plus the
# lepton's GenLepton::Kind (-1 if hadronic). genTop_pt is the input of the top pT reweighting,
# which is a shape weight: it has to be defined before the event selection, where the
# denominators are summed, so this runs from defineGenVariables, not from addAllVariables.
# The per-top arrays must not share the TTInfo_ prefix with the scalars of addGenProcessInfo:
# FuseAnaTuples stores all columns of one prefix as one collection.
def addGenTopInfo(dfw, gen_info):
    if "TT" not in gen_info:
        return
    DeclareHeader(
        os.path.join(os.environ["FLAF_PATH"], "include", "GenProcess", "TT.h")
    )
    dfw.Define(
        "_genTopInfo",
        "gen_process::tt::identify(GenPart_pdgId, GenPart_statusFlags,"
        " GenPart_genPartIdxMother, GenPart_pt, GenPart_eta, GenPart_phi,"
        " GenPart_mass)",
    )
    for slot in range(2):
        dfw.Define(
            f"_genTop_lep{slot}_p4",
            "reco_tau::gen_truth::lastCopyP4ByGenPartIndex(genLeptons,"
            f" _genTopInfo.lep_index[{slot}])",
        )
    p4s = {
        "genTop": ("_genTopInfo.top_p4[0]", "_genTopInfo.top_p4[1]"),
        "genTop_b": ("_genTopInfo.b_p4[0]", "_genTopInfo.b_p4[1]"),
        "genTop_lep": ("_genTop_lep0_p4", "_genTop_lep1_p4"),
    }
    for prefix, (from_top, from_antitop) in p4s.items():
        for var in ["pt", "eta", "phi", "mass"]:
            if prefix == "genTop_b" and var == "mass":
                continue  # always zero in NanoAOD
            dfw.DefineAndAppend(
                f"{prefix}_{var}",
                f"ROOT::VecOps::RVec<float>{{static_cast<float>({from_top}.{var}()),"
                f" static_cast<float>({from_antitop}.{var}())}}",
            )
    dfw.DefineAndAppend(
        "genTop_lep_gen_kind",
        "ROOT::VecOps::RVec<int>{"
        "reco_tau::gen_truth::kindByGenPartIndex(genLeptons, _genTopInfo.lep_index[0]),"
        " reco_tau::gen_truth::kindByGenPartIndex(genLeptons, _genTopInfo.lep_index[1])}",
    )
