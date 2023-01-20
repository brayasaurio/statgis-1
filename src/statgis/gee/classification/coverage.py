"""Classify pixels in images"""
import ee

ee.Initialize()


def water_coverage(
    image: ee.Image,
    blue: str,
    green: str,
    red: str,
    nir: str,
    swir: str,
) -> ee.Image:
    """
    Function to classify pixels as water based on Based on Zou et al. (2017) and
    Worder & Beurs (2020).

    Parameters
    ----------
    image : ee.Image
        Image to classify.

    blue : str
        Blue band name.

    green : str
        Green band name.

    red : str
        Red band name.

    nir : str
        Near infrared band name.

    swir : str
        Short-wave infrared band name.

    Returns
    -------
    image : ee.Image
        Image with water coverage band classified where water pixels are 1 and
        no-water are 0.
    """
    mndwi = image.expression(
        f"(b('{green}') - b('{swir}'))/(b('{green}') + b('{swir}'))"
    ).rename("mNDWI")
    ndvi = image.expression(
        f"(b('{nir}') - b('{red}'))/(b('{nir}') + b('{red}'))"
    ).rename("NDVI")
    evi = image.expression(
        f"2.5*(b('{nir}') - b('{red}'))/(b('{nir}') + 6*b('{red}') - 7.5*b('{blue}') + 1)"
    ).rename("EVI")

    water = (
        evi.lt(0.1)
           .And(mndwi.gt(evi).Or(mndwi.gt(ndvi)))
           .rename("WATER_COVERAGE")
    )

    image = image.addBands(water)

    return image


def vegetation_coverage(
    image: ee.Image,
    blue: str,
    red: str,
    nir: str,
    swir: str,
) -> ee.Image:
    """
    Function to classify pixels as vegetation based on Based on Zou et al. (2017)
    and Worder & Beurs (2020).

    Parameters
    ----------
    image : ee.Image
        Image to classify.

    blue : str
        Blue band name.

    green : str
        Green band name.

    red : str
        Red band name.

    nir : str
        Near infrared band name.

    swir : str
        Short-wave infrared band name.

    Returns
    -------
    image : ee.Image
        Image with vegettaion coverage band classified where vegetation pixels
        are 1 and no-vegetation are 0.
    """
    ndbi = image.expression(
        f"(b('{swir}') - b('{nir}'))/(b('{swir}') + b('{nir}'))"
    ).rename("NDBI")
    ndvi = image.expression(
        f"(b('{nir}') - b('{red}'))/(b('{nir}') + b('{red}'))"
    ).rename("NDVI")
    evi = image.expression(
        f"2.5*(b('{nir}') - b('{red}'))/(b('{nir}') + 6*b('{red}') - 7.5*b('{blue}') + 1)"
    ).rename("EVI")

    vegetation = (
        evi.gte(0.1)
           .And(ndvi.gte(0.2).And(ndbi.lt(0.0)))
           .rename("VEGETATION_COVERAGE")
    )

    image = image.addBands(vegetation)

    return image
