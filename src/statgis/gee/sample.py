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
    """
    N = image_collection.size().getInfo()
    ic_list = image_collection.toList(N)

    data = []

    for i in range(N):
        image = ee.Image(ic_list.get(i))
        values = sample_image(image, band=band, geom=geom, scale=scale)
        data.append(values)

    return data
