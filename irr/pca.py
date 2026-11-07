"""PCA on daily yield curve changes and PCA-based curve shocks."""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .curve import to_years

PC_NAMES = ["PC1 (Level)", "PC2 (Slope)", "PC3 (Curvature)"]


@dataclass
class YieldPCA:
    loadings: pd.DataFrame          # tenors x PCs, in standardized space
    explained_variance: pd.Series   # share of variance per PC
    scores: pd.DataFrame            # daily PC scores
    dy_std: pd.Series               # std dev of daily changes per tenor


def fit_pca(yields: pd.DataFrame, n_components: int = 3) -> YieldPCA:
    """Run PCA (via SVD) on standardized daily yield changes."""
    dy = yields.diff().dropna()
    dy_std = dy.std()
    X = ((dy - dy.mean()) / dy_std).values

    U, S, Vt = np.linalg.svd(X, full_matrices=False)
    eigvals = S**2 / (X.shape[0] - 1)

    # SVD signs are arbitrary. Fix them so PC1 is a rise in rates and PC2 is a
    # steeper curve (long end up). This makes the results stable between runs.
    for k in range(min(2, n_components)):
        flip = Vt[k].sum() < 0 if k == 0 else Vt[k][-1] < Vt[k][0]
        if flip:
            Vt[k] *= -1
            U[:, k] *= -1

    cols = [f"PC{i + 1}" for i in range(n_components)]
    return YieldPCA(
        loadings=pd.DataFrame(Vt[:n_components].T, index=dy.columns, columns=cols),
        explained_variance=pd.Series(eigvals / eigvals.sum(), index=[f"PC{i + 1}" for i in range(len(S))]),
        scores=pd.DataFrame(U[:, :n_components] * S[:n_components], index=dy.index, columns=cols),
        dy_std=dy_std,
    )


def pc_shock(model: YieldPCA, pc: str, n_std: float = 2.0) -> pd.Series:
    """Yield change per tenor (decimal) for an n_std move in one PC's score."""
    size = n_std * model.scores[pc].std()
    return size * model.loadings[pc] * model.dy_std


def pc_shocked_curves(model: YieldPCA, curve_by_label: pd.Series, n_std: float = 2.0) -> dict[str, pd.Series]:
    """Shocked curves (indexed by years) for PC1..PC3."""
    return {
        name: to_years(curve_by_label + pc_shock(model, pc, n_std))
        for name, pc in zip(PC_NAMES, model.loadings.columns)
    }
