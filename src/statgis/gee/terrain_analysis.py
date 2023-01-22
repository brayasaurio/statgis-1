"""Get hypsometric curves from a DEM"""
import ee
import numpy as np
from numpy.typing import ArrayLike
from .sample import sample_image


ee.Initialize()


def hypsometric_curve(
    catchment: ee.Geometry,
    dem: ee.Image,
    scale: float,
    band: str,
    bins: int = 100,
) -> list[ArrayLike]:
    """
    Calculate the cumulative area and comulative height from a catchment for the
    hypsometric curve.

    Parameters
    ----------
    catchment : ee.Geometry
        Catchment area to analyse.

    dem : ee.Image
        Digital elevation model (DEM) to analyse.

    scale : float
        Scale of DEM.

    band : str
        Band of DEM with elevetaion information.

    bins : int
        Number of bins for cumalitive area an height.

    Returns
    -------
    area : ArrayLike
        Normalized area.

    height : ArrayLike
        Normalized height.
    """
    dem = dem.select(band)

    values = sample_image(dem, catchment, scale, band)
    values = values/values.max()

    area, height = np.histogram(values, bins=np.linspace(0, 1, bins+1))

    area = 1 - np.flip(area.cumsum()/area.cumsum().max())
    height = np.flip(height[:-1])

    return area, height
