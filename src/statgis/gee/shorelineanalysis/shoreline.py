"""Extract shoreline from images"""
import ee


ee.Initialize()


def shoreline_characterization(
    image: ee.Image,
    region: ee.Geometry,
    scale: float,
    band: str,
) -> ee.FeatureCollection:
    """
    Extract shoreline from image classified.

    Parameters
    ----------
    image : ee.Image
        Classified image to analyse.

    region : ee.Geometry
        Region of interest to clip the image and shorelines.

    scale : float
        Image scale.

    band : str
        Band of interest.

    Returns
    -------
    polylines : ee.FeatureCollection
        Digitalized shorelines from images.
    """
    def polygon_to_polyline(geom):
        """convert polygon to polyline"""
        coords = geom.geometry().simplify(maxError=scale).coordinates()
        buffer = ee.Number(scale).multiply(-1)

        polyline = geom.setGeometry(
            ee.Geometry.MultiLineString(coords)
                       .intersection(region.buffer(buffer))
        )

        return polyline

    image = image.select(band)

    polygon = image.clip(region).reduceToVectors(scale=scale)       # Polygonize image
    polygon = polygon.filter(ee.Filter.eq("label", 0))              # Select land

    polylines = polygon.map(polygon_to_polyline)

    return polylines
