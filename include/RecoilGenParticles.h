#pragma once

#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <vector>

#include <ROOT/RVec.hxx>
#include <Math/Vector4D.h>
#include <Math/VectorUtil.h>

// Bosonic recoil corrections: https://cms-higgs-leprare.docs.cern.ch/htt-common/V_recoil/

namespace recoil_boson {

using RVecF = ROOT::RVec<float>;
using RVecI = ROOT::RVec<int>;
using RVecU = ROOT::RVec<unsigned short>;
using LorentzVectorM = ROOT::Math::PtEtaPhiMVector;

inline bool IsNeutrino(const int pdgId) {
    const int absPdgId = std::abs(pdgId);
    return absPdgId == 12 || absPdgId == 14 || absPdgId == 16; // also 18 for nu'_tau ?
}

inline bool IsChargedLepton(const int pdgId) {
    const int absPdgId = std::abs(pdgId);
    return absPdgId == 11 || absPdgId == 13 || absPdgId == 15;
}

inline bool PassRecoilGenParticleSelection(const int pdgId, const int status, const unsigned short statusFlags, const bool includeNeutrinos) 
{
    // Required inputs: https://indico.cern.ch/event/1583951/contributions/6751916/attachments/3159171/5612627/HLepRare_25.10.22.pdf
    // - pick stable charged leptons and neutrinos which are fromHardProcess
    // - pick anything with bit 10 = isDirectHardProcessTauDecayProduct

    if (status != 1) return false;

    const bool fromHardProcess = (statusFlags >> 8) & 0x1;
    const bool isDirectHardProcessTauDecayProduct = (statusFlags >> 10) & 0x1;

    const bool isChargedLep = IsChargedLepton(pdgId);
    const bool isNeutrino = IsNeutrino(pdgId);

    if (fromHardProcess) {
        if (isChargedLep) return true;
        if (includeNeutrinos && isNeutrino) return true;
    }

    if (isDirectHardProcessTauDecayProduct) {
        if (!includeNeutrinos && isNeutrino) return false; // skip neutrinos from tau decays if not including neutrinos.
        return true; // include all direct tau decay products (charged leptons and neutrinos)
    }

    return false;

}

inline LorentzVectorM GetGenBosonP4(const RVecF& pt, const RVecF& eta, const RVecF& phi,
                                    const RVecF& mass, const RVecI& pdgId, const RVecI& status,
                                    const RVecU& statusFlags)
{
    const std::size_t n = pt.size();
    if (eta.size() != n || phi.size() != n || mass.size() != n || pdgId.size() != n || 
        status.size() != n || statusFlags.size() != n) {
        throw std::runtime_error("GetGenBosonP4: inconsistent GenPart collection sizes");
    }

    LorentzVectorM p4(0., 0., 0., 0.);
    for (std::size_t i = 0; i < n; ++i) {
        if (!PassRecoilGenParticleSelection(pdgId[i], status[i], statusFlags[i], true)) continue;
        p4 += LorentzVectorM(pt[i], eta[i], phi[i], mass[i]);
    }

    return p4;
}

inline LorentzVectorM GetGenBosonVisP4(const RVecF& pt, const RVecF& eta, const RVecF& phi,
                                       const RVecF& mass, const RVecI& pdgId, const RVecI& status,
                                       const RVecU& statusFlags)
{
    const std::size_t n = pt.size();
    if (eta.size() != n || phi.size() != n || mass.size() != n || pdgId.size() != n || 
        status.size() != n || statusFlags.size() != n) {
        throw std::runtime_error("GetGenBosonVisP4: inconsistent GenPart collection sizes");
    }

    LorentzVectorM p4(0., 0., 0., 0.);
    for (std::size_t i = 0; i < n; ++i) {
        if (!PassRecoilGenParticleSelection(pdgId[i], status[i], statusFlags[i], false)) continue;
        p4 += LorentzVectorM(pt[i], eta[i], phi[i], mass[i]);
    }

    return p4;
}

inline int GetRecoilNJet(const RVecF& genJet_pt, const RVecF& genJet_eta)
{
    // recoil jet multiplicity with recommended threshold

    if (genJet_pt.size() != genJet_eta.size()) {
        throw std::runtime_error("GetRecoilNJet: inconsistent GenJet collection sizes (between pt and eta)");
    }

    int njet = 0;
    for (std::size_t i = 0; i < genJet_pt.size(); ++i) {
        const float pt = genJet_pt[i];
        const float abs_eta = std::abs(genJet_eta[i]);
        const bool horn_region = abs_eta > 2.5f && abs_eta < 3.0f;
        const bool passed = horn_region ? (pt > 50.f) : (pt > 30.f);

        if (passed) ++njet;
    }
    return njet;
}

inline float GetRecoilNJetFloat(const RVecF& genJet_pt, const RVecF& genJet_eta)
{
    return static_cast<float>(GetRecoilNJet(genJet_pt, genJet_eta));
    // correctionlib recoil payload requires real value (must be converted to float value for technical reasons)
}

inline float GetRecoilNJetCategoryFloat(const RVecF& genJet_pt, const RVecF& genJet_eta)
{
    const int njet = GetRecoilNJet(genJet_pt, genJet_eta);
    if (njet == 0) return 0.f;
    if (njet == 1) return 1.f;
    return 2.f; // 2 or more jets are merged into one category for recoil corrections
}

} // namespace recoil_boson