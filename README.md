# StatGIS Python Package

![PyPI](https://img.shields.io/pypi/v/statgis) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/statgis?color=yellow) [![Documentation Status](https://readthedocs.org/projects/statgis/badge/?version=latest)](https://statgis.readthedocs.io/en/latest/?badge=latest)

StatGIS help to the users to process and analyse satellite images in Google Earth Engine.

## Installation

```bash
$ pip install statgis
```

## Usage

In this package you could find function to scale optical images, classify images,
characterize shorelines and much more.

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
