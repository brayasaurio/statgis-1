# statgis

Tools for improve work with geospatial data in Python

## Installation

```bash
$ pip install statgis
```

## Usage

StatGIS help to the users to process and analyse satellite images in Google Earth Engine.

```python
# Example: mask clouds and scale to reflectance values
import ee
from statgis.gee import landsat_functions

ee.Initialize()

image_collection = (
    ee.ImageCollection("LANDSAT/LC09/C02/T1_L2")
      .map(landsat_functions.cloud_mask)
      .map(landsat_functions.scaler)
)
```

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`statgis` was created by Sebástian Narváez-Salcedo, Brayan Navarro-Londoño. It is licensed under the terms of the MIT license.

## Credits

`statgis` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
