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
    """

    band_number = image.bandNames().size()

    return image.set("bands", band_number)
