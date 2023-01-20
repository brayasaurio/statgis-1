"""Test sample submodule"""
import ee
import pandas as pd
from statgis.gee.zonal_statistics import zonal_statistics_collection

ee.Initialize()

coords = [-70.025, -55.409, -65.487, -53.400]
roi = ee.Geometry.BBox(*coords)

sentinel_2 = (
    ee.ImageCollection("COPERNICUS/S2_SR")
      .filterBounds(roi)
      .filterDate("2020-01-01", "2020-04-01")
)

def test_zs():
    data = zonal_statistics_collection(sentinel_2, roi, 100000, ["B4", "B3", "B2"])

    assert isinstance(data, pd.DataFrame)