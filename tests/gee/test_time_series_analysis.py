import ee
import numpy as np
import statgis.gee.time_series_analysis as tsa

ee.Initialize()

coords = [-70.025, -55.409, -65.487, -53.400]
roi = ee.Geometry.BBox(*coords)

sentinel_2 = (
    ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(roi)
        .map(lambda img: img.addBands(img.normalizedDifference(["B5", "B4"]).rename("NDVI")))
)

tsp_codes = ['time', 'NDVI', 'predicted', 'detrended', 'seasonal', 'anomaly']

first_date = sentinel_2.first().get("system:time_start").getInfo()
first_date = np.array(first_date, dtype="datetime64[ms]")

years = [year for year in range(2018, 2022+1)]


def test_extract_dates():
    """Test extract dates"""

    dates = tsa.extract_dates(sentinel_2)

    assert dates.values[0] == first_date


def test_reduce_by_year():
    """Test reduce by year"""
    iy = tsa.reduce_by_year(sentinel_2, ee.Reducer.mean(), 2018, 2022)
    iy = (
        iy.reduceColumns(ee.Reducer.toList(), ["year"])
          .get("list")
          .getInfo()
    )

    assert years == iy


def test_tsp():
    """Test time series processing and dependencies"""
    ic, mm = tsa.time_series_processing(sentinel_2, "NDVI")

    assert [b["id"] for b in ic.first().getInfo()["bands"]] == tsp_codes
    