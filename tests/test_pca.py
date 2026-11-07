import pytest

from irr.pca import fit_pca, pc_shock


def test_explained_variance(yields):
    ev = fit_pca(yields).explained_variance
    assert ev.sum() == pytest.approx(1.0)
    assert ev["PC1"] > ev["PC2"] > ev["PC3"]
    assert ev.iloc[:3].sum() > 0.8


def test_signs_are_fixed(yields):
    model = fit_pca(yields)
    assert (pc_shock(model, "PC1") > 0).all()   # level: every tenor rises
    pc2 = model.loadings["PC2"]
    assert pc2["30Y"] > pc2["1M"]               # slope: long end up vs short end
