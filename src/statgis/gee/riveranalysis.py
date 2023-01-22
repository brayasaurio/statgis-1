"""Analyse rivers with sattelite images"""
import ee

ee.Initialize()


def plume_characterization(
    image: ee.Image,
    sample_region: ee.Geometry,
    blue: str,
    green: str,
    red: str,
    nir: str,
) -> ee.Image:
    """
    Extract river plume from an image based on the colors in a sample region.

    Parameters
    ----------
    Image : ee.Image
        Image to be classified.

    sample_region : ee.Geometry
        Polygon that enclosess a region of the Image that the user indetifies as
        river plume.

    blue : str
        Blue band name.

    green : str
        Green band name.

    red : str
        Red band name.

    nir : str
        Near infrared band name.

    Returns
    -------
    image : ee.Image
        Plume characterized in the three color bands.
    """
    image = image.addBands(
        image.expression(
            f"(b('{green}') - b('{nir}'))/(b('{green}') + b('{nir}'))"
        ).rename("NDWI"),
        None,
        True,
    )

    mask = image.select("NDWI").gt(0)
    image = image.updateMask(mask)

    reducer = ee.Reducer.min().combine(reducer2=ee.Reducer.max(), sharedInputs=True)

    limits = image.select([blue, green, red]).reduceRegion(
        reducer=reducer, geometry=sample_region, scale=30
    )

    image = image.addBands(
        image.expression(
            f"(b('{blue}') > MINI && b('{blue}') < MAXI) ? 1 : 0",
            {
                "MAXI": limits.getNumber(blue + "_max"),
                "MINI": limits.getNumber(blue + "_min"),
            },
        ).rename("plume_blue"),
        None,
        True,
    )

    image = image.addBands(
        image.expression(
            f"(b('{green}') > MINI && b('{green}') < MAXI) ? 1 : 0",
            {
                "MAXI": limits.getNumber(green + "_max"),
                "MINI": limits.getNumber(green + "_min"),
            },
        ).rename("plume_green"),
        None,
        True,
    )

    image = image.addBands(
        image.expression(
            f"(b('{red}') > MINI && b('{red}') < MAXI) ? 1 : 0",
            {
                "MAXI": limits.getNumber(red + "_max"),
                "MINI": limits.getNumber(red + "_min"),
            },
        ).rename("plume_red"),
        None,
        True,
    )

    image = image.addBands(
        image.expression(
            "(b('plume_blue') + b('plume_green') + b('plume_red'))"
        ).rename("plume"),
        None,
        True,
    )

    plume_mask = image.select("plume").gt(0.5)

    pixel_count = plume_mask.select(0).connectedPixelCount(100, False)
    count_mask = pixel_count.select(0).gt(50)

    image = image.updateMask(plume_mask).updateMask(count_mask)

    return image
