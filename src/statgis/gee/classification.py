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


def clean_boolean_classification(
    image: ee.Image,
    scale: float,
    band: str,
    true_class_threshold: float,
    false_class_threshold: float,
) -> ee.Image:
    """
    Clean boolean coverage classification counting the neighbors pixels and filter
    those which surpass their respective thresholds.

    Parameters
    ----------
    image : ee.Image
        Boolean classification raster to clean.

    scale : float
        Image scale to perform the process.

    band : str
        Band name with the classification.

    true_class_threshold : float
        Threshold for true values to conserve an entity.

    false_class_threshold : float
        Threshold for false values to conserve an entity.

    Returns
    -------
    filled : ee.Image
        Boolean classification image cleaned.
    """
    image = image.select(band).toInt()

    connected_false = ee.Number(true_class_threshold).divide(scale).int()
    connected_true = ee.Number(false_class_threshold).divide(scale).int()

    false_filled = (
        image.addBands(image)
        .reduceConnectedComponents(ee.Reducer.median(), band, connected_false)
        .unmask(99)
        .eq(99)
        .And(image.neq(0))
    )

    filled = (
        false_filled.addBands(false_filled)
        .reduceConnectedComponents(ee.Reducer.median(), band+"_1", connected_true)
        .unmask(99)
        .eq(99)
        .And(false_filled.neq(1))
    )

    filled = filled.expression("b(0) == 0 ? 1 : 0").rename(band)

    return filled
