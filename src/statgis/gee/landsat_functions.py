"""
Function to process Landsat SR Images.
"""
import ee


def scaler(image: ee.Image) -> ee.Image:
    """
    Scale optical bands to surface reflectance values and thermal bands to Kelvin.

    Parameters
    ----------
    image : ee.Image
        Landsat SR image.

    Returns
    -------
    image : ee.Image
        Image with bands scaled.
    """
    optical = image.select("SR_B.").multiply(0.0000275).add(-0.2)
    thermal = image.select("ST_B.*").multiply(0.00341802).add(149)

    image = image.addBands(optical, None, True).addBands(thermal, None, True)

    return image


def cloud_mask(image: ee.Image, mask_snow: bool = False) -> ee.Image:
    """
    Mask pixels classified as clouds from QA_PIXEL band.

    Parameters
    ----------
    image : ee.Image
        Image to mask.

    mask_snow : bool (optional)
        If `True` mask pixels classified as snow.
        If `False` mask only pixels classified as cloud.

    Returns
    -------
    image : ee.Image
        Masked image.
    """
    qa = image.select("QA_PIXEL")

    cirrus = qa.bitwiseAnd((1 << 2)).eq(0)
    cloud = qa.bitwiseAnd((1 << 3)).eq(0)
    shadow = qa.bitwiseAnd((1 << 4)).eq(0)
    snow = qa.bitwiseAnd((1 << 5)).eq(0)

    image = image.updateMask(cirrus).updateMask(cloud).updateMask(shadow)

    if mask_snow:
        image = image.updateMask(snow)

    return image


def rename_bands(image: ee.Image) -> ee.Image:
    """
    Rename the bands from a Landsat Image.

    Parameters
    ----------
    image : ee.Image
        Image of interest.

    Returns
    -------
    image : ee.Image
        Image with bands renamed
    """
    prop_toa = ["QA_PIXEL", "QA_RADSAT", "SAA", "SZA", "VAA", "VZA"]
    prop_sr5 = ["SR_ATMOS_OPACITY", "SR_CLOUD_QA", "ST_ATRAN", "ST_CDIST", "ST_DRAD", "ST_EMIS", "ST_EMSD", "ST_QA",
                "ST_TRAD", "ST_URAD", "QA_PIXEL", "QA_RADSAT"]
    prop_sr8 = ["SR_QA_AEROSOL"] + prop_sr5[2:]

    color_5_toa = ["BLUE", "GREEN", "RED", "NIR", "SWIR1", "TIR", "SWIR2"]
    color_7_toa = color_5_toa[:-2] + ["TIR1", "TIR2", "SWIR2", "PANCHROMATIC"]
    color_8_toa = ["AEROSOL"] + color_5_toa[:-2] + ["SWIR2", "PANCHROMATIC", "CIRRUS", "TIR1", "TIR2"]

    color_5_sr = ["BLUE", "GREEN", "RED", "NIR", "SWIR1", "SWIR2", "TEMPERATURE"]
    color_8_sr = ["AEROSOL"] + color_5_sr

    idx = ee.String(image.get("LANDSAT_PRODUCT_ID"))
    sensor_number = ee.Number.parse(idx.slice(3, 4))
    processing_level = ee.Number.parse(idx.slice(6, 7))

    color_bands = ee.Algorithms.If(
        condition=processing_level.eq(1),
        trueCase=image.select("B.+").bandNames(),
        falseCase=image.select(".+B.+").bandNames(),
    )

    property_bands = ee.Algorithms.If(
        condition=processing_level.eq(1),
        trueCase=prop_toa,
        falseCase=ee.Algorithms.If(
            condition=sensor_number.lte(7),
            trueCase=prop_sr5,
            falseCase=prop_sr8,
        )
    )

    new_names = ee.Algorithms.If(
        condition=processing_level.eq(1),
        trueCase=ee.Algorithms.If(
            condition=sensor_number.eq(5),
            trueCase=color_5_toa,
            falseCase=ee.Algorithms.If(
                condition=sensor_number.eq(7),
                trueCase=color_7_toa,
                falseCase=color_8_toa,
            )
        ),
        falseCase=ee.Algorithms.If(
            condition=sensor_number.lte(7),
            trueCase=color_5_sr,
            falseCase=color_8_sr,
        )
    )

    image = image.select(color_bands).rename(new_names).addBands(image.select(property_bands))

    return image
