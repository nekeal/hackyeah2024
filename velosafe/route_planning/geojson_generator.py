import geojson
from geojson import GeoJSON

from velosafe.route_planning.point import Point


class GeoJsonGenerator:
    def __init__(self, points: list[Point]):
        self.points = points

    def generate(self) -> GeoJSON:
        features = []

        for point in self.points:
            feature = geojson.Feature(geometry=geojson.Point(tuple(point)))
            features.append(feature)

        return geojson.FeatureCollection(features)
