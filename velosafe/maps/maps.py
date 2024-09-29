import folium
from folium.plugins import MarkerCluster
from gpx_converter import Converter


class MapService:
    def __init__(self, starting_location=None, zoom_start=13):
        self.map = folium.Map(location=starting_location, zoom_start=zoom_start, zoom_control=False)

    def fit_bounds(self):
        self.map.fit_bounds(self.map.get_bounds())

    def add_start_finish_markers(self, start, finish):
        folium.Marker(start).add_to(self.map)
        folium.Marker(finish).add_to(self.map)

    def add_route_from_gpx(self, gpx_file):
        dic = Converter(input_file=gpx_file).gpx_to_dictionary(latitude_key="latitude", longitude_key="longitude")

        points = []
        for index in range(len(dic["latitude"])):
            points.append([dic["latitude"][index], dic["longitude"][index]])

        route = folium.PolyLine(points, color="blue", weight=4, opacity=1)
        route.add_child(folium.Popup("inline explicit Popup"))
        self.add_start_finish_markers(points[0], points[-1])

        route.add_to(self.map)

    def add_route_from_geojson(self, data, style_function=None, color=None):
        if color:
            style_function = lambda x: {"color": color}

        folium.GeoJson(data, style_function=style_function).add_to(self.map)

    def get_html(self):
        return self.map.get_root().render()

    def save_to_file(self):
        self.map.save("index.html")


# map_service = MapService()
# map_service.add_route_from_gpx("mapa.gpx")
# map_service.fit_bounds()
# map_service.save_to_file()
