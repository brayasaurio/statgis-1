"""Submodule for genarate statistical plots"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from typing import Union
from matplotlib.axes import Axes
from matplotlib.ticker import NullLocator
from numpy.typing import ArrayLike
from .stats import corr_matrix


def plot_corr_matrix(
    data: pd.DataFrame,
    variables: ArrayLike | None = None,
    half: bool = False,
    hide_insignificants: bool = False,
    significant_threshold: float = 0.05,
    show_labels: bool = True,
    show_colorbar: bool = False,
    palette: str = "Spectral",
    text_color: str = "black",
    ax: Union[Axes, None] = None,
) -> Axes:
    """
    Calculate the pearson correlation matrix of the variables in a dataframe.

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe with the variables to evaluate their correlation.

    variables : ArrayLike | None = None
        The variables of interest, if it is not defined, all variables in
        the dataframe will be evaluated.

    half : bool (optional)
        If True, only show the corerlation of the first half of the matrix,
        excluding the repeated correlation.

    hide_insignifcants : bool (optional)
        If True, hide all the correlation with a p-value greater than the
        significant threshold.

    significant_threshold : float (optional)
        Threshold of significant correlation.

    show_labels : bool (optional)
        Show the correlation value.

    show_colorbar : bool (optional)
        Show colorbar

    palette : str (optional)
        Color palette for correlation plot.

    text_color : str (optional)
        Color of text correlation labels.

    ax : matplotlib.axes.Axes | None (optional)
        Axes to draw the correlation matrix.
    returns
    -------
    ax : matplotlib.axes.Axes
        Correltion matrix.
    """
    # If variables are not defined get all columns from data
    if variables is None:
        variables = data.columns

    # Get the number of variables
    N = len(variables)

    # Reverse variables for plot
    reverse = variables[::-1]

    # Get the correlation matrix
    corr = corr_matrix(
        data, variables, half, hide_insignificants, significant_threshold
    )

    # If there not axes create one
    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

    # Plot matrix with pcolormesh
    im = ax.pcolormesh(
        variables, reverse, corr, cmap=palette, edgecolor="w", vmin=-1, vmax=1
    )

    # Invert y axis
    ax.invert_yaxis()

    # Add the colorbar
    if show_colorbar:
        cax = ax.inset_axes([1.04, 0.1, 0.05, 0.8])
        bar = plt.colorbar(im, cax=cax, label="Correlation")

    if show_labels:
        x, y = np.meshgrid(np.arange(N), np.arange(N))
        x = x.reshape(-1)
        y = y.reshape(-1)
        t = corr.values.reshape(-1)

        for xi, yi, ti in zip(x, y, t):
            if np.isfinite(ti):
                ax.text(
                    xi, yi,
                    round(ti, 2),
                    color=text_color,
                    size=8,
                    ha="center",
                    va="center",
                )

    ax.xaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_minor_locator(NullLocator())

    return ax