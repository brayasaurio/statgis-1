"""Functions to process image collections as time series"""
import ee
import pandas as pd

ee.Initialize()


def extract_dates(image_collection: ee.ImageCollection) -> pd.DatetimeIndex:
    """
    Extract dates from all images in an image collection.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Collection of image.

    Returns
    -------
    dates : pd.Series
        Series with the dates of the images.
    """
    dates = (
        image_collection.reduceColumns(ee.Reducer.toList(), ["system:time_start"])
        .get("list")
        .getInfo()
    )

    dates = pd.DatetimeIndex(pd.to_datetime(dates, unit="ms"))

    return dates


def resample(image_collection: ee.ImageCollection, reducer: ee.Reducer, scale: str, ) -> ee.ImageCollection:
    """
    Function to resample an Image Collection to a fixed timestamp.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Image Collection to resample.

    reducer : ee.Reducer
        To aggregate the images

    scale : str
        Time scale to aggregate the image, must be one from:
        - annual.
        - monthly.
        - monthly-stat.
        - monthly-stat-repeated.

    Returns
    -------
    final_collection : ee.ImageCollection
        Collection resampled.
    """

    dates = image_collection.reduceColumns(
        reducer=ee.Reducer.min().combine(ee.Reducer.max(), sharedInputs=True),
        selectors=["system:time_start"],
    ).getInfo()

    for key, val in dates.items():
        dates[key] = ee.Date(val).get("year").getInfo()

    months = range(1, 13)
    years = range(dates["min"], dates["max"] + 1)

    band_names = image_collection.first().bandNames()

    final_collection = []

    if scale == "annual":
        for year in years:
            date = ee.Date.fromYMD(year, 1, 1).millis()

            image = (
                image_collection.filter(ee.Filter.calendarRange(year, year, "year"))
                .reduce(reducer, 4)
                .set("year", year)
                .set("system:time_start", date)
            )

            final_collection.append(image)

    elif scale == "monthly":
        for year in years:
            for month in months:
                date = ee.Date.fromYMD(year, month, 1).millis()

                image = (
                    image_collection.filter(ee.Filter.calendarRange(year, year, "year"))
                    .filter(ee.Filter.calendarRange(month, month, "month"))
                    .reduce(reducer, 4)
                    .set("year", year)
                    .set("month", month)
                    .set("system:time_start", date)
                )

                final_collection.append(image)

    elif scale == "monthly-stat":
        for month in months:
            image = (
                image_collection.filter(ee.Filter.calendarRange(month, month, "month"))
                .reduce(reducer, 4)
                .set("month", month)
            )

            final_collection.append(image)

    elif scale == "monthly-stat-repeated":
        for year in years:
            for month in months:
                date = ee.Date.fromYMD(year, month, 1).millis()

                image = (
                    image_collection.filter(ee.Filter.calendarRange(month, month, "month"))
                    .reduce(reducer, 4)
                    .set("year", year)
                    .set("month", month)
                    .set("system:time_start", date)
                )

                final_collection.append(image)

    else:
        Exception("ERROR")

    final_collection = ee.ImageCollection(final_collection).map(lambda img: img.rename(band_names))

    return final_collection


def detrend(image_collection: ee.ImageCollection, band: str, restore_mean: bool = True) -> ee.ImageCollection:
    """
    Calculate the linear trend and seasonality of an image collection.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Image collection to remove its trend.

    band : str
        Band of interest.

    restore_mean : bool = True
        If `True`, the data mean wil lbe restored in the seasonality.

    Returns
    -------
    image_collection : ee.ImageCollection
        Image collection with linear trend and seasonality.

    """
    image_collection = image_collection.map(lambda img: img.addBands(img.metadata("system:time_start").rename("time")))
    image_collection = image_collection.select(["time", band])

    mean = image_collection.select(band).mean()

    fitted = image_collection.reduce(ee.Reducer.linearFit())

    def add_prediction(image: ee.Image) -> ee.Image:
        """Add the predicted values with the linear fitted parameters"""
        predicted = image.select("time").multiply(fitted.select("scale")).add(fitted.select("offset")).rename(
            "predicted")

        return image.addBands(predicted)

    def add_seasonality(image: ee.Image) -> ee.Image:
        """Add the seasonality removing the prediction from the raw data"""
        seasonality = image.select(band).subtract(image.select("predicted")).rename("seasonality")

        if restore_mean:
            seasonality = seasonality.add(mean).rename("seasonality")

        return image.addBands(seasonality)

    image_collection = image_collection.map(add_prediction).map(add_seasonality)

    return image_collection


def seasonal_decompose(image_collection: ee.ImageCollection, band: str, restore_mean: bool = True) -> ee.ImageCollection:
    """
    Seasonal decomposition using the linear trend. This function take an image collection
    and extract the time series components in the specified band.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Image collection of interest.

    band : str
        Band of interest.

    restore_mean : bool = True
        If `True`, the data mean wil lbe restored in the seasonality.

    Returns
    -------
    final_collection : ee.ImageCollection
        Image collection with time series components.
    """
    image_collection = detrend(image_collection, band, restore_mean)

    def calculate_anomalies(detrended_collection: ee.ImageCollection) -> ee.ImageCollection:
        """Add the anomalies to a detrended image collection"""
        mean_repeated_collection = resample(detrended_collection, ee.Reducer.mean(), "monthly-stat-repeated")

        dates = mean_repeated_collection.reduceColumns(ee.Reducer.toList(), ["system:time_start"]).getInfo()["list"]

        final_collection = []

        for date in dates:
            image = detrended_collection.filter(ee.Filter.eq("system:time_start", date)).first()
            mean_repeated = mean_repeated_collection.filter(ee.Filter.eq("system:time_start", date)).first()

            image = (
                image.addBands(mean_repeated.select("seasonality").rename("seasonality_repeated"))
                .addBands(image.select("seasonality").subtract(mean_repeated.select("seasonality")).rename("anomalies"))
            )

            final_collection.append(image)

        final_collection = ee.ImageCollection(final_collection)

        return final_collection

    image_collection = calculate_anomalies(image_collection)

    return image_collection
