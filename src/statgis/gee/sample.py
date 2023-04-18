"""Sample pixel values from image in a region of interest"""
import ee
import numpy as np
from numpy.typing import ArrayLike


ee.Initialize()


def sample_image(
    image: ee.Image,
    geom: ee.Geometry,
    scale: float,
    band: str,
) -> ArrayLike:
    """
    Sample all pixels from an image in the specified band.

    Parameters
    ----------
    image : ee.Image
        Image to sample.

    geom : ee.Geometry
        Region of interest.

    scale : float
        Scale of image to sample.

    band : str
        Band of interest.

    Returns
    -------
    data : np.array
        Array with the sampled values.
    
    Example
    -------
    >>> import ee
    >>> from statgis.gee import sample, landsat_functions, time_series_analysis
    >>> ee.Initialize()
    >>> roi = ee.Geometry.BBox(-76.6854802, 3.3903932, -76.6904802, 3.3953932)
    >>> landsat_collection = ee.ImageCollection([])
    >>> for code in ["LT05", "LE07", "LC08", "LC09"]:
    ...     landsat_collection = landsat_collection.merge(
    ...         ee.ImageCollection(f"LANDSAT/{code}/C02/T1_L2")
    ...         .filterBounds(roi)
    ...         .filterDate("1995-01-01", "2022-12-31")
    ...         .map(landsat_functions.scaler)
    ...         .map(landsat_functions.cloud_mask)
    ...         .map(landsat_functions.rename_bands)
    ...         .map(lambda img: img.addBands(img.normalizedDifference(["NIR", "RED"]).rename("NDVI")))
    ...     )
    >>> image = landsat_collection.mean()
    >>> mean_ndvi_values = sample.sample_image(image, roi, 30, "NDVI")
    """
    image = image.select(band)

    try:
        sample = image.sampleRegions(collection=geom, scale=scale, geometries=False)

        sample = sample.toList(sample.size())
        raw = sample.getInfo()

        data = np.array([r["properties"][band] for r in raw])
    except:
        data = np.array([np.nan])

    return data


def sample_collection(
    image_collection: ee.ImageCollection,
    geom: ee.Geometry,
    scale: float,
    band: str,
) -> list:
    """
    This function sample all images in an image collection applying the sample_image
    function to all images.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Image collection to sample.

    geom : ee.Geometry
        Region of interest.

    scale : float
        Scale of image to sample.

    band : str
        Band of interest.

    Returns
    -------
    data : list
        list of np.array with all the sampled values per image.
    
    Example
    -------
    >>> import ee
    >>> from statgis.gee import sample, landsat_functions, time_series_analysis
    >>> ee.Initialize()
    >>> roi = ee.Geometry.BBox(-76.6854802, 3.3903932, -76.6904802, 3.3953932)
    >>> landsat_collection = ee.ImageCollection([])
    >>> for code in ["LT05", "LE07", "LC08", "LC09"]:
    ...     landsat_collection = landsat_collection.merge(
    ...         ee.ImageCollection(f"LANDSAT/{code}/C02/T1_L2")
    ...         .filterBounds(roi)
    ...         .filterDate("1995-01-01", "2022-12-31")
    ...         .map(landsat_functions.scaler)
    ...         .map(landsat_functions.cloud_mask)
    ...         .map(landsat_functions.rename_bands)
    ...         .map(lambda img: img.addBands(img.normalizedDifference(["NIR", "RED"]).rename("NDVI")))
    ...     )
    >>> annual_ndvi = time_series_analysis.resample(landsat_collection, ee.Reducer.median(), "annual")
    >>> annual_ndvi_values = sample.sample_collection(annual_ndvi, roi, 30, "NDVI")
    """
    N = image_collection.size().getInfo()
    ic_list = image_collection.toList(N)

    data = []

    for i in range(N):
        image = ee.Image(ic_list.get(i))
        values = sample_image(image, band=band, geom=geom, scale=scale)
        data.append(values)

    return data
