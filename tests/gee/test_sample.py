"""Test sample submodule"""
import ee
from statgis.gee.time_series_analysis import reduce_by_month
from statgis.gee.sample import sample_collection

ee.Initialize()

coords = [-70.025, -55.409, -65.487, -53.400]
roi = ee.Geometry.BBox(*coords)

sentinel_2 = ee.ImageCollection("COPERNICUS/S2_SR").filterBounds(roi)
monthly_mean = reduce_by_month(sentinel_2.select("B1"), ee.Reducer.mean())

def test_sample():
    """Test sample collection and sample image"""
    samples = sample_collection(monthly_mean, roi, 1000000, "seasonal")

    assert len(samples) == 12

test_sample()