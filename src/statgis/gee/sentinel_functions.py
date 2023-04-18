"""
Function to process Sentinel-2 images.
"""
import ee

def scaler(image: ee.Image) -> ee.Image:
    """
    Scale bands from Sentinel-2 image.

    Parameters
    ----------
    image : ee.Image
        Sentinel-2 image to scale.

    Returns
    -------
    image : ee.Image
        Image with bands scaled.
    
    Example
    -------
    ```python
    import ee
    from statgis.gee import sentinel_functions

    ee.Initialize()

    poi = ee.Geometry.Point(-75.6636142, 6.2443677)
    image = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(poi)
        .first()
    )

    image = sentinel_functions.scaler(image)
    ```

    Or
    
    ```python
    import ee
    from statgis.gee import sentinel_functions

    ee.Initialize()

    poi = ee.Geometry.Point(-75.6636142, 6.2443677)
    image_collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(poi)
        .map(sentinel_functions.scaler)
    )
    ```
    """
    bands = image.select("B.*").divide(10000)
    image = image.addBands(bands, None, True)

    return image


def cloud_mask(image: ee.Image) -> ee.Image:
    """
    Mask clouds from Sentinel-2 image using QA60 band.

    Parameters
    ----------
    Image : ee.Image
        Image to mask.

    Returns
    -------
    Image : ee.Image
        Masked image.
    
    Example
    -------
    ```python
    import ee
    from statgis.gee import sentinel_functions

    ee.Initialize()

    poi = ee.Geometry.Point(-75.6636142, 6.2443677)
    image = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(poi)
        .first()
    )

    image = sentinel_functions.cloud_mask(image)
    ```

    Or

    ```python
    import ee
    from statgis.gee import sentinel_functions

    ee.Initialize()

    poi = ee.Geometry.Point(-75.6636142, 6.2443677)
    image_collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(poi)
        .map(sentinel_functions.cloud_mask)
    )
    ```
    """
    qa = image.select("QA60")

    clouds = qa.bitwiseAnd((1 << 10)).eq(0)
    cirrus = qa.bitwiseAnd((1 << 11)).eq(0)

    image = image.updateMask(clouds).updateMask(cirrus)

    return image
