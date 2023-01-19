"""Test functions from gee.landsat_functions submodule"""

import ee
from statgis.gee.landsat_functions import cloud_mask, scaler

ee.Initialize()

def cloud_mask_2(img):
    """Simplofy cloud mask function to hide snow without the parameter"""

    return cloud_mask(img, True)

def test_landsat_function():
    """Test scaler and cloud_mask functions"""

    coords = [-70.025, -55.409, -65.487, -53.400]

    roi = ee.Geometry.BBox(*coords)
    landsat_8_1 = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
          .filterBounds(roi)
          .map(cloud_mask)
          .map(scaler)
    )

    landsat_8_2 = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
          .filterBounds(roi)
          .map(cloud_mask_2)
          .map(scaler)
    )

    img_1 = landsat_8_1.mean()
    img_2 = landsat_8_2.mean()

    assert isinstance(img_1, ee.Image) and isinstance(img_2, ee.Image)
