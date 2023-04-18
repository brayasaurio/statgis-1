"""Reduce images in a region of interest"""
from typing import Sequence, Union
import ee
import pandas as pd


ee.Initialize()


def zonal_statistics_image(
    image: ee.Image,
    geom: ee.Geometry,
    scale: float,
    bands: Union[Sequence[str], str] = "all",
    reducer: Union[ee.Reducer, str] = "all",
    tile_scale: int = 16,
) -> pd.DataFrame:
    """
    Function to calculate a statistic in the specified region for one image.

    Parameters
    ----------
    image : ee.Image
        Image of interest.

    geom : ee.Geometry
        Region of interest to reduce the image.

    scale : float
        Pixel size for the sample to perform the zonal statistics.

    bands : Sequence | str (optional)
        List, tuple with the bands of interest or, if you only want one band, the name
        of the band. By default, the process takes into consideration all bands.

    reducer : ee.Reducer | str (optional)
        Reducer to apply to the image. By default, image are reduced to its, mean, standard
        deviation, maximum, minimum, and count.

    tile_scale : int (optional)
        Scale of the mosaic to allow EarthEngine to split the task to more cores.

    Returns
    -------
    data : pandas.DataFrame
        DataFrame with all the stats for all specified bands.

    Example
    -------
    ```python
    import ee
    from statgis.gee import zonal_statistics

    ee.Initialize()

    roi = ee.Geometry.BBox(-75.2671803, 4.4104561 ,-75.2691803, 4.4124561)
    mean_precipitation_2022 = (
        ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        .filterDate("2022-01-01", "2022-12-31")
        .mean()
    )

    stats = zonal_statistics.zonal_statistics_image(mean_precipitation_2022, roi, 30, "precipitation")
    ```
    """
    if bands != "all":
        image = image.select(bands)

    if reducer == "all":
        reducer = ee.Reducer.mean().combine(
            ee.Reducer.stdDev().combine(
                ee.Reducer.max().combine(
                    ee.Reducer.min().combine(ee.Reducer.count(), sharedInputs=True),
                    sharedInputs=True,
                ),
                sharedInputs=True,
            ),
            sharedInputs=True,
        )

    stats = image.reduceRegion(
        reducer=reducer, geometry=geom, scale=scale, tileScale=tile_scale
    )
    stats = stats.set("system:time_start", image.get("system:time_start"))

    data = pd.DataFrame(stats.getInfo(), index=[0])
    data["date"] = pd.DatetimeIndex(
        pd.to_datetime(data["system:time_start"], unit="ms").dt.date
    )

    return data


def zonal_statistics_collection(
    image_collection: ee.ImageCollection,
    geom: ee.Geometry,
    scale: float,
    bands: Union[Sequence[str], str] = "all",
    reducer: Union[ee.Reducer, str] = "all",
    tile_scale: int = 16,
) -> pd.DataFrame:
    """
    Function to calculate a statistic in the specified region for all Image in an image
    collection.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Image Collection with the image to reduce.

    geom : ee.Geometry
        Region of interest to reduce the images.

    scale : float
        Pixel size for the sample to perform the zonal statistics.

    bands : Sequence | str (optional)
        List, tuple with the bands of interest or, if you only want one band, the name
        of the band. By default, the process takes into consideration all bands.

    reducer : ee.Reducer | str (optional)
        Reducer to apply to all image. By default, image are reduced to its, mean, standard
        deviation, maximum, minimum, and count.

    tile_scale : int (optional)
        Scale of the mosaic to allow EarthEngine to split the task to more cores.

    Returns
    ------
    data : pandas.DataFrame
        DataFrame with all the stats for all specified bands.
        
    Example
    -------
    ```python
    import ee
    from statgis.gee import zonal_statistics

    ee.Initialize()

    roi = ee.Geometry.BBox(-75.2671803, 4.4104561 ,-75.2691803, 4.4124561)
    chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY").filterDate("2022-01-01", "2022-12-31")

    daily_mean_precipitation = zonal_statistics.zonal_statistics_collection(
        chirps, roi, 30, "precipitation", ee.Reducer.mean()
    )
    ```
    """
    if bands != "all":
        image_collection = image_collection.select(bands)

    if reducer == "all":
        reducer = ee.Reducer.mean().combine(
            ee.Reducer.stdDev().combine(
                ee.Reducer.max().combine(
                    ee.Reducer.min().combine(ee.Reducer.count(), sharedInputs=True),
                    sharedInputs=True,
                ),
                sharedInputs=True,
            ),
            sharedInputs=True,
        )

    def reduce_image(image):
        stats = image.reduceRegion(
            reducer=reducer, geometry=geom, scale=scale, tileScale=tile_scale
        )

        stats = ee.Feature(geom, stats)
        stats = stats.set("system:time_start", image.get("system:time_start"))

        return stats

    fc = ee.FeatureCollection(image_collection.map(reduce_image))

    entries = [feature["properties"] for feature in fc.getInfo()["features"]]

    data = pd.DataFrame(entries)
    data["date"] = pd.DatetimeIndex(
        pd.to_datetime(data["system:time_start"], unit="ms").dt.date
    )

    return data
