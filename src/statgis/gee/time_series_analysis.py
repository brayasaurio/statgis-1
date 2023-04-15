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


def trend(image_collection: ee.ImageCollection, band: str) -> ee.ImageCollection:
    """
    Calculate the linear trend and seasonal variation to an image collection.

    Parameters
    ----------
    image_collection : ee.imageCollection
        Image collection to perform the linear trend and detrend.

    band : str
        Name of the band to perform the calc.

    Returns
    -------
    image_collection : ee.ImageCollection
        Image collection with the Raw data, Time, Trend and seasonal variation bands.
    """

    def time_func(image: ee.Image) -> ee.Image:
        """Calculate time band for linear regression"""
        time = (
            image.metadata("system:time_start")
            .divide(1000 * 60 * 60 * 24 * 365)
            .rename("time")
        )

        return image.addBands(time)

    mean = image_collection.select(band).mean()

    image_collection = image_collection.map(time_func)
    image_collection = image_collection.select(["time", band])

    fitted = image_collection.reduce(ee.Reducer.linearFit())

    def pred_func(image: ee.Image) -> ee.Image:
        """Calculate linear regression"""
        pred = (
            image.select("time")
            .multiply(fitted.select("scale"))
            .add(fitted.select("offset"))
            .rename("predicted")
            .toFloat()
        )

        return image.addBands(pred)

    def stat_func(image: ee.Image) -> ee.Image:
        """Calculate the seasonal component"""
        stat = image.expression(
            "band - pred + mean",
            {
                "band": image.select(band),
                "pred": image.select("predicted"),
                "mean": mean,
            },
        ).rename("detrended").toFloat()

        return image.addBands(stat)

    image_collection = image_collection.map(pred_func).map(stat_func)

    return image_collection


# TODO: change the reduce_by_year function with the resample function from JS
def reduce_by_year(
    image_collection: ee.ImageCollection,
    reducer: ee.Reducer,
    start: int,
    end: int,
) -> ee.ImageCollection:
    """
    Resample image collection to annual reduced collection.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Image collection to reduce.

    reducer : ee.Reducer
        To apply through the image collection.

    start : int
        First year.

    end : int
        Last year.

    Returns
    -------
    annual_collection : ee.ImageCollection
        Image collection reduced to annual frequency.
    """
    annual_collection = []

    for year in range(start, end + 1):
        img = (
            image_collection.filter(ee.Filter.calendarRange(year, year, "year"))
            .reduce(reducer)
            .set("year", year)
        )

        annual_collection.append(img)

    return ee.ImageCollection(annual_collection)


def reduce_by_month(
        image_collection: ee.ImageCollection,
        reducer: ee.Reducer,
) -> ee.ImageCollection:
    """
    Reduce image collection to monthly statistic.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Image collection to reduce.

    reducer : ee.Reducer
        To apply through image collection.

    Returns
    -------
    monthly_collection : ee.ImageCollection
        Image collection reduced to monthly frequency.
    """
    monthly_collection = []

    for month in range(1, 13):
        img = (
            image_collection.filter(ee.Filter.calendarRange(month, month, "month"))
            .reduce(reducer)
            .rename("seasonal")
            .set("month", month)
        )

        monthly_collection.append(img)

    return ee.ImageCollection(monthly_collection)


def calculate_anomalies(
        image_collection: ee.ImageCollection, monthly_mean: ee.ImageCollection
) -> ee.ImageCollection:
    """
    Calculate the anomalies of a ImageCollection subtracting the monthly mean values.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Image collection trended by the trend function to calc the anomalies.

    monthly_mean : ee.ImageCollection
        Image collection with the monthly means of ImageCollection calculated by the
        `reduce_by_month` function.

    Returns
    -------
    anomalies : ee.ImageCollection
        ImageCollection with seasonal means added and anomalies calculated.
    """

    def calc_anomaly(image: ee.Image) -> ee.Image:
        """Function for calculate anomalies."""
        anomaly = image.expression(
            "stat - mean",
            {"stat": image.select("detrended"), "mean": image.select("seasonal")},
        ).rename("anomaly")

        return image.addBands(anomaly)

    m01 = image_collection.filter(ee.Filter.calendarRange(1, 1, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 1)).first())
    )
    m02 = image_collection.filter(ee.Filter.calendarRange(2, 2, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 2)).first())
    )
    m03 = image_collection.filter(ee.Filter.calendarRange(3, 3, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 3)).first())
    )
    m04 = image_collection.filter(ee.Filter.calendarRange(4, 4, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 4)).first())
    )
    m05 = image_collection.filter(ee.Filter.calendarRange(5, 5, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 5)).first())
    )
    m06 = image_collection.filter(ee.Filter.calendarRange(6, 6, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 6)).first())
    )
    m07 = image_collection.filter(ee.Filter.calendarRange(7, 7, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 7)).first())
    )
    m08 = image_collection.filter(ee.Filter.calendarRange(8, 8, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 8)).first())
    )
    m09 = image_collection.filter(ee.Filter.calendarRange(9, 9, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 9)).first())
    )
    m10 = image_collection.filter(ee.Filter.calendarRange(10, 10, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 10)).first())
    )
    m11 = image_collection.filter(ee.Filter.calendarRange(11, 11, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 11)).first())
    )
    m12 = image_collection.filter(ee.Filter.calendarRange(12, 12, "month")).map(
        lambda x: x.addBands(monthly_mean.filter(ee.Filter.eq("month", 12)).first())
    )

    anomalies = (
        m01.merge(m02)
        .merge(m03)
        .merge(m04)
        .merge(m05)
        .merge(m06)
        .merge(m07)
        .merge(m08)
        .merge(m09)
        .merge(m10)
        .merge(m11)
        .merge(m12)
    )

    anomalies = anomalies.sort("system:time_start")
    anomalies = anomalies.map(calc_anomaly)

    return anomalies


def time_series_processing(
        image_collection: ee.ImageCollection, band: str
) -> tuple[ee.ImageCollection, ee.ImageCollection]:
    """
    This function take an ee.ImageCollection and calculate the linear trend, the
    detrended component, the seasonal mean and anomalies for the selected band.
    To calculate the linear trend the function use `ee.Reducer.linearFit()`, next,
    calculate the detrended component subtracting the linear_fitted values to the
    original series and restoring its mean, the monthly means are calculated by
    selecting all the image in the specific month and reduce it by its mean, finally,
    subtracting the monthly means to the detrended component anomalies are obtained.
    This function work as a "wrapper" function of `trend()`, `reduce_by_month()` and
    `calc_anomalies()`.

    Parameters
    ----------
    image_collection : ee.ImageCollection
        Image collection to process.

    band : str
        Name of the band of interest.

    Returns
    -------
    data : ee.ImageCollection
        Image collection with the raw data, the linear trend, detrended component,
        seasonal mean and the anomalies.

    monthly_mean : ee.ImageCollection
        Image collection with the twelves monthly means calculated.
    """
    trended = trend(image_collection, band)
    monthly_mean = reduce_by_month(trended.select("detrended"), ee.Reducer.mean())
    data = calculate_anomalies(trended, monthly_mean)

    return data, monthly_mean
