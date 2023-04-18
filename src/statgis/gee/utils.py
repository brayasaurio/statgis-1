"""Some image operations"""

from typing import Union
import ee

ee.Initialize()


def calculate_covered_area(image: ee.Image, region: Union[ee.geometry, ee.Feature], scale: float) -> ee.Image:
    """
    Calculate the total covered area by an image in a specific region and add it as an attribute.

    Parameters
    ----------
    image : ee.Image
        Image of interest.

    region : ee.Geometry | ee.Feature
        Region of interest.

    scale : float
        Image scale

    Returns
    -------
    image : ee.Image
        Image with covered area attribute

    Example
    -------
    Calculate the covered area by an image in an region:

    >>> import ee
    >>> from statgis.gee import landsat_functions, utils
    >>> ee.Initialize()
    >>> roi = ee.Geometry.BBox(-74.2726232, 4.6486206, -74.2776232, 4.6536206)
    >>> image = (
    ...     ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    ...     .map(landsat_functions.scaler)
    ...     .map(landsat_functions.cloud_mask)
    ...     .map(landsat_functions.rename_bands)
    ...     .first()
    ... )
    >>> image = utils.calculate_covered_area(image, roi, 30)

    Whit a `lambda` function we can calculate the covered area by all image in a collection:

    >>> import ee
    >>> from statgis.gee import landsat_functions, utils
    >>> ee.Initialize()
    >>> roi = ee.Geometry.BBox(-74.2726232, 4.6486206, -74.2776232, 4.6536206)
    >>> image_collection = (
    ...     ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    ...     .map(landsat_functions.scaler)
    ...     .map(landsat_functions.cloud_mask)
    ...     .map(landsat_functions.rename_bands)
    ...     .map(lambda img: utils.calculate_covered_area(img, roi, 30))
    ... )
    """
    covered_area_list = image.reduceRegion(
        reducer=ee.Reducer.count(),
        geometry=region,
        scale=scale,
        bestEffort=True,
        tileScale=16,
    ).values()

    covered_area = ee.Number(ee.Algorithms.If(
        condition=covered_area_list.size().gt(0),
        trueCase=covered_area_list.get(0),
        falseCase=0,
    )).multiply(scale * scale)

    percentage_covered_area = ee.Number(ee.Algorithms.If(
        condition=covered_area.divide(region.area(scale)).multiply(100).lte(100),
        trueCase=covered_area.divide(region.area(scale)).multiply(100),
        falseCase=100.0,
    ))

    image = (
        image.set("COVERED_AREA", covered_area)
        .set("PERCENTAGE_COVERED_AREA", percentage_covered_area)
    )

    return image


def calculate_band_number(image: ee.Image) -> ee.Image:
    """
    Calculate the number of bands for an image.
    Parameters
    ----------
    image : ee.Image
        Image of interest.

    Returns
    -------
    image : ee.Image
        Image with band number as an attribute.

    Example
    -------
    Calculate the number of bands for an image:
    
    >>> import ee
    >>> from statgis.gee import landsat_functions, utils
    >>> ee.Initialize()
    >>> roi = ee.Geometry.BBox(-74.2726232, 4.6486206, -74.2776232, 4.6536206)
    >>> image = (
    ...     ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    ...     .map(landsat_functions.scaler)
    ...     .map(landsat_functions.cloud_mask)
    ...     .map(landsat_functions.rename_bands)
    ...     .first()
    ... )
    >>> image = utils.calculate_band_number(image)

    Calculate the number of bands for all images in a collection:

    >>> import ee
    >>> from statgis.gee import landsat_functions, utils
    >>> ee.Initialize()
    >>> roi = ee.Geometry.BBox(-74.2726232, 4.6486206, -74.2776232, 4.6536206)
    >>> image_collection = (
    ...     ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
    ...     .map(landsat_functions.scaler)
    ...     .map(landsat_functions.cloud_mask)
    ...     .map(landsat_functions.rename_bands)
    ...     .map(utils.calculate_band_number)
    ... )
    """
    band_number = image.bandNames().size()

    return image.set("bands", band_number)
