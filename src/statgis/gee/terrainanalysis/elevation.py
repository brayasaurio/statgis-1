"""Get hypsometric curves from a DEM"""
import ee


ee.Initialize()


def hypsometric_curve(
    catchment: ee.Geometry,
    dem: ee.Image,
    band: str = "elevation",
    samples: int = 20,
    scale: float = 30,
    max_pixels: int = 1e19,
) -> list[list]:
    """
    Function to calculate the hypsometric curve of a catchment by a feature.
    Parameters
    ----------
    catchment  : ee.Geometry
        Basin extent in interest region.

    dem : ee.Image
        Digital elevation model.

    samples: float
        this parameter define the resolution of height seperation for area calculator.

    scale: float
        this factor depend of the resolution and de area extend of interest region.

    Returns
    -------
    list_data : list
        output the area and heigth normalized.
    """
    # Extract the basin extent with catchment
    dem = dem.clip(catchment)

    # Extract the Minimum and Maximum Elevation and total area (in pixels) of DEM
    reducer = ee.Reducer.min().combine(
        reducer2=ee.Reducer.max().combine(
            reducer2=ee.Reducer.count(), sharedInputs=True
        ),
        sharedInputs=True,
    )

    limits = dem.select([band]).reduceRegion(
        reducer=reducer, geometry=catchment, scale=scale, maxPixels = max_pixels
    )

    # define the range between minimum and maximum elevation for normalitation
    range_ = (
        limits.getNumber(band + "_max").getInfo()
        - limits.getNumber(band + "_min").getInfo()
    ) / samples

    area = [1]
    height = [0]

    for i in range(samples):
        mask = (
            dem.select(band)
            .gte(limits.getNumber(band + "_min").getInfo())
            .And(
                dem.select(band).lte(
                    limits.getNumber(band + "_min").getInfo() + range_ * (i + 1)
                )
            )
        )

        # this funtion count the pixel count of the height subrange
        reducer1 = ee.Reducer.sum()

        sub_pixels = mask.select([band]).reduceRegion(
            reducer=reducer1, geometry=catchment, scale=scale, maxPixels = max_pixels
        )

        sub_pixels = sub_pixels.getNumber(band).getInfo()

        height.append(((i) + 1 / 2) / samples)

        area.append(1 - (sub_pixels / limits.getNumber(band + "_count").getInfo()))

    list_data = [area, height]

    return list_data
