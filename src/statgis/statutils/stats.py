"""Submodule to ease some statisticals"""
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from numpy.typing import ArrayLike


def corr_matrix(
    data: pd.DataFrame,
    variables: ArrayLike | None = None,
    half: bool = False,
    hide_insignificants: bool = False,
    singificant_threshold: float = 0.05,
) -> pd.DataFrame:
    """
    Calculate the pearson correlation matrix of the variables in a dataframe.
    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with the variables to evaluate their correlation.
    variables : ArrayLike | None = None
        The variables of interest, if it is not defined, all variables in
        the dataframe will be evaluated.
    half : bool = False
        If True, only show the corerlation of the first half of the matrix,
        excluding the repeated correlation.
    hide_insignifcants : bool = False
        If True, hide all the correlation with a p-value greater than the
        significant threshold.
    siginificant_threshold : float = 0.05
        Threshold of significant correlation.
    returns
    -------
    corr : pd.DataFrame
        Dataframe with the correlation values.
    """
    if variables is None:
        variables = data.columns

    reverse = variables[::-1]

    N = len(variables)

    corr = np.empty((N, N))
    pval = np.full((N, N), np.nan)
    mask = np.full((N, N), np.nan)

    for i, iv in enumerate(variables):
        for j, jv in enumerate(reverse):
            c, p = pearsonr(data[iv], data[jv])
            corr[j, i] = c

            if p <= singificant_threshold:
                pval[j, i] = 1.0

        mask[: N - i, i] = 1.0

    if half:
        corr *= mask

    if hide_insignificants:
        corr *= pval

    corr = pd.DataFrame(data=corr, index=reverse, columns=variables)

    return corr
