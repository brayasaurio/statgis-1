"""Test functions from gee.sentinel_functions submodule"""
import ee
from statgis.gee.sentinel_functions import cloud_mask, scaler

ee.Initialize()

def test_sentinel_function():
    """Test scaler and cloud_mask functions"""
    coords = [-70.025, -55.409, -65.487, -53.400]

    roi = ee.Geometry.BBox(*coords)
    sentinel_2 = (
        ee.ImageCollection("COPERNICUS/S2_SR")
          .filterBounds(roi)
          .map(cloud_mask)
          .map(scaler)
    )

    img = sentinel_2.mean()

    assert isinstance(img, ee.Image)
