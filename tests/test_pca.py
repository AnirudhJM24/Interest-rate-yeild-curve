import pytest

from irr.pca import fit_pca, pc_shock


def test_explained_variance(yields):
    ev = fit_pca(yields).explained_variance
    assert ev.sum() == pytest.approx(1.0)
    assert ev["PC1"] == pytest.approx(0.6537, abs=1e-3)
    assert ev.iloc[:3].sum() == pytest.approx(0.8872, abs=1e-3)


def test_signs_are_fixed(yields):
    model = fit_pca(yields)
    assert (pc_shock(model, "PC1") > 0).all()          # level: every tenor rises
    pc2 = model.loadings["PC2"]
    assert pc2["30Y"] > 0 > pc2["3M"]                   # slope: long end up, short end down
