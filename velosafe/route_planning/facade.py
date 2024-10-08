import copy
import time
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Annotated

import geojson
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from functools import reduce
import networkx as nx
import osmnx as ox

from velosafe.route_planning.geojson_generator import GeoJsonGenerator
from velosafe.route_planning.point import Point
from velosafe.route_planning.street_data import StreetData
from velosafe.route_planning.mocks import StreetDataMocks
from velosafe.route_planning.weights import Weights
from velosafe.route_planning.route import Route
from velosafe.maps.maps import MapService


class GeneralRoadTypes(TextChoices):
    road = "road", _("Road")
    street = "street", _("Street")
    track = "track", _("Track")
    bike_path = "bike_path", _("Bike path")


class LinkTypes(TextChoices):
    primary = "primary", _("primary link")
    residential = "residential", _("residential link")
    primary_link = "primary_link", _("primary link")
    service = "service", _("service link")
    secondary = "secondary", _("secondary link")
    tertiary = "tertiary", _("tertiary link")
    pedestrian = "pedestrian", _("pedestrian link")
    track = "track", _("track link")
    cycleway = "cycleway", _("cycle way link")
    unclassified = "unclassified", _("unclassified link")
    path = "path", _("path link")
    living_street = "living_street", _("living street link")


@dataclass(frozen=True)
class RoutePlanningPreferences:
    max_allowed_speed: Annotated[int, "km/h"] = 200
    street_light: bool | None = None
    allowed_road_types: list[GeneralRoadTypes] = field(
        default_factory=lambda: [m for m in GeneralRoadTypes.__members__.values()]
    )
    safety_factor: int = 1  # 1-5, 1 - fast, 5 - safe
    bike_path_preference: int = 1  # 1-5 1 - bike lanes and roads treated the same, 5 - bike lanes preferred
    car_traffic_factor: int = 1 # 1-5, 1 - car traffic not affecting, 5 - avoid big traffic on the streets


@dataclass(frozen=True)
class RoutePlanningInput:
    points: list[Point]
    preference: RoutePlanningPreferences

def timing_val(func):
    def wrapper(*arg, **kw):
        '''source: http://www.daniweb.com/code/snippet368.html'''
        t1 = time.time()
        res = func(*arg, **kw)
        t2 = time.time()
        print(f'Function: {func.__name__}, Time: {t2 - t1}')
        return res
    return wrapper


class RoutePlanningFacade:
    G = None

    @classmethod
    @timing_val
    def _get_G(cls, city):
        if cls.G is None:
            G = StreetData.download(city)
            G = StreetData.consolidate_intersections(G)
            G = StreetData.fill_max_speed(G)
            cls.G = G
        return copy.deepcopy(cls.G)

    @classmethod
    @timing_val
    def plan_route(cls, input: RoutePlanningInput) -> geojson.GeoJSON:
        print("Calculating route", input)
        G = cls._get_G('Nowy Targ')
        # G = StreetData.download("Nowy Targ")
        # G = StreetData.consolidate_intersections(G)
        # G = StreetData.fill_max_speed(G)
        G_car = G.copy()
        G = StreetData.remove_streets_exceeding_max_speed(G, input.preference.max_allowed_speed)
        G = StreetData.remove_disallowed_road_types(G, input.preference.allowed_road_types)
        G = StreetDataMocks.mock_street_lights(G)

        G_car = StreetData.remove_disallowed_road_types(G_car, allowed_road_types=['road', 'street'])
        _, car_edges = ox.graph_to_gdfs(G_car)
        car_edges['car_traffic'] = nx.edge_betweenness_centrality(G_car, weight='weight', k=1000)
        car_edges['car_traffic'] = car_edges['car_traffic'] / max(car_edges['car_traffic'])

        nodes, edges = ox.graph_to_gdfs(G)
        print(car_edges['car_traffic'].index)
        edges['car_traffic'] = 0
        edges['car_traffic'] = car_edges['car_traffic']
        G = ox.graph_from_gdfs(nodes, edges)

        W = Weights(input.preference.safety_factor, input.preference.bike_path_preference, input.preference.car_traffic_factor)
        G = Weights.apply_weights(G, W.get_weight_by_roadtype, W.get_weight_by_maxspeed, W.get_weight_by_length)

        routes = []
        print(input.points)
        for a, b in zip(input.points[:-1], input.points[1:]):
            start_node = StreetData.get_closest_node_id(G, a)
            end_node = StreetData.get_closest_node_id(G, b)

            routes.append(Route.find(G, start_node, end_node))

        G = reduce(lambda r1, r2: nx.disjoint_union(r1, r2), routes)
        print(G)

        nodes, edges = ox.graph_to_gdfs(G)

        M = MapService(ox.geocode("Nowy Targ"))
        color_map = {
            "cycleway": "blue",
            "path": "blue",
            "pedestrian": "green",
            "track": "blue",
            "residential": "red",
            "living_street": "red",
            "service": "red",
            "tertiary": "red",
            "secondary": "black",
            "primary": "black",
            "other": "red",
            "primary_link": "black",
            "secondary_link": "black",
            "tertiary_link": "red",
            "unclassified": "red",
        }
        for key, color in color_map.items():
            sub_nodes, sub_edges = ox.graph_to_gdfs(G)
            filtered_edges = sub_edges[sub_edges["highway"] == key]
            if filtered_edges.empty:
                continue
            print(filtered_edges)
            sub_G = ox.graph_from_gdfs(sub_nodes, filtered_edges)
            style_function = (lambda x: {"color": color})
            _, sub_e = ox.graph_to_gdfs(sub_G)
            M.add_route_from_geojson(sub_e, style_function=style_function)
            

        sub_nodes, sub_edges = ox.graph_to_gdfs(G)
        filtered_edges = sub_edges[sub_edges["highway"].isin(color_map.keys()) == False]
        if filtered_edges.empty:
            return M.get_html()
        sub_G = ox.graph_from_gdfs(sub_nodes, filtered_edges)
        style_function = (lambda x: {"color": color})
        _, sub_e = ox.graph_to_gdfs(sub_G)
        M.add_route_from_geojson(sub_e, style_function=style_function)
        print(M.map)

        return M.get_html()
    
    @staticmethod
    def get_bike_traffic(preference: RoutePlanningPreferences):
        # Yes, I like pipes xD
        G = StreetData.download('Nowy Targ')
        G = StreetData.consolidate_intersections(G)
        G = StreetData.fill_max_speed(G)
        G = StreetData.remove_streets_exceeding_max_speed(G, preference.max_allowed_speed)
        G = StreetData.remove_disallowed_road_types(G, preference.allowed_road_types)
        G = StreetDataMocks.mock_street_lights(G)

        nodes, edges = ox.graph_to_gdfs(G)

        edges['traffic'] = nx.edge_betweenness_centrality(G, weight='weight', k=1000)
        edges['traffic'] = edges['traffic'] / max(edges['traffic'])
        edges = edges[edges['traffic'] > 0.15]

        M = MapService(ox.geocode('Nowy Targ'))
        M.add_route_from_geojson(edges)

        return M.get_html()

if __name__ == "__main__":
    facade = RoutePlanningFacade()
    # points = [[50.0676907, 19.9902774], [50.06764, 19.9891], [50.06763, 19.98882], [50.0676261, 19.9888154], [50.06758, 19.98883], [50.06746, 19.98885], [50.06733, 19.98887], [50.06689, 19.98892], [50.06637, 19.98898], [50.06609, 19.98901], [50.06589, 19.98902], [50.06548, 19.9891], [50.06531, 19.98913], [50.06501, 19.98922], [50.06477, 19.98931], [50.0646, 19.9894], [50.06446, 19.9895], [50.0644588, 19.9894977], [50.06443, 19.98934], [50.06439, 19.98901], [50.06438, 19.98894], [50.06432, 19.98862], [50.0643, 19.98853], [50.06423, 19.98818], [50.06419, 19.98796], [50.06417, 19.98787], [50.06415, 19.98774], [50.06412, 19.9876], [50.06391, 19.98655], [50.06389, 19.98649], [50.0638, 19.98605], [50.06373, 19.9857], [50.06369, 19.98551], [50.06365, 19.98531], [50.06362, 19.98522], [50.06356, 19.985], [50.06351, 19.98484], [50.06341, 19.98454], [50.06336, 19.98442], [50.06327, 19.98419], [50.0632, 19.98403], [50.06312, 19.98387], [50.06309, 19.9838], [50.06296, 19.98356], [50.06276, 19.9832], [50.0626, 19.98288], [50.06245, 19.98256], [50.06228, 19.98222], [50.06212, 19.98187], [50.0621, 19.98183], [50.06162, 19.98081], [50.06156, 19.98067], [50.06148, 19.98051], [50.06116, 19.97981], [50.06104, 19.97956], [50.06094, 19.97935], [50.06082, 19.97914], [50.06056, 19.97861], [50.06026, 19.97797], [50.06019, 19.97783], [50.06012, 19.97767], [50.06003, 19.9774], [50.05992, 19.97701], [50.05984, 19.97671], [50.0598, 19.97649], [50.05976, 19.97628], [50.05972, 19.97598], [50.05969, 19.97579], [50.05967, 19.97559], [50.05966, 19.97544], [50.05965, 19.9752], [50.05966, 19.97502], [50.05966, 19.97478], [50.05967, 19.97457], [50.05968, 19.97442], [50.05972, 19.97415], [50.05974, 19.97397], [50.05983, 19.97361], [50.05989, 19.97338], [50.05995, 19.97315], [50.06018, 19.97226], [50.06028, 19.97185], [50.06053, 19.97077], [50.06056, 19.97065], [50.06059, 19.97047], [50.0606, 19.97045], [50.06061, 19.97037], [50.06066, 19.96998], [50.06067, 19.96967], [50.06067, 19.96955], [50.06066, 19.96945], [50.06065, 19.96934], [50.06063, 19.96914], [50.06061, 19.96896], [50.06058, 19.96879], [50.06056, 19.96867], [50.06054, 19.96856], [50.0605, 19.96838], [50.0604, 19.96796], [50.06039, 19.96791], [50.06028, 19.96748], [50.06022, 19.96722], [50.06017, 19.96701], [50.06014, 19.96691], [50.05994, 19.9661], [50.05971, 19.96516], [50.05965, 19.96491], [50.05944, 19.96401], [50.05938, 19.96377], [50.05932, 19.96357], [50.05926, 19.96333], [50.05918, 19.96308], [50.05917, 19.96305], [50.05906, 19.96274], [50.05895, 19.96246], [50.05877, 19.96204], [50.05864, 19.96174], [50.05858, 19.96162], [50.05836, 19.96113], [50.05822, 19.9608], [50.05817, 19.96067], [50.05804, 19.96029], [50.05798, 19.9601], [50.05796, 19.96003], [50.05794, 19.95999], [50.05793, 19.95994], [50.05793, 19.95991], [50.05792, 19.95984], [50.05791, 19.95977], [50.05791, 19.95968], [50.05791, 19.95959], [50.0579081, 19.9595949], [50.05793, 19.95951], [50.05795, 19.95943], [50.05797, 19.95937], [50.05801, 19.95924], [50.05804, 19.95917], [50.05806, 19.9591], [50.05807, 19.95906], [50.05808, 19.95902], [50.05808, 19.95896], [50.05808, 19.95891], [50.05808, 19.95885], [50.05807, 19.9588], [50.05806, 19.95875], [50.05805, 19.9587], [50.05804, 19.95869], [50.05791, 19.95852], [50.05785, 19.95844], [50.05783, 19.95839], [50.05781, 19.95832], [50.05779, 19.95827], [50.05777, 19.95822], [50.05775, 19.95815], [50.05773, 19.95809], [50.05771, 19.95802], [50.0577, 19.95794], [50.05763, 19.95747], [50.05761, 19.95729], [50.0576, 19.95724], [50.0576, 19.95719], [50.0576, 19.95712], [50.05761, 19.95696], [50.05763, 19.95681], [50.05765, 19.95672], [50.05766, 19.95665], [50.05767, 19.95664], [50.05768, 19.95661], [50.05768, 19.95658], [50.0578, 19.95625], [50.05792, 19.95591], [50.05817, 19.95528], [50.0583, 19.9549], [50.05835, 19.95475], [50.05842, 19.95452], [50.05845, 19.9544], [50.0585, 19.95418], [50.05856, 19.95389], [50.05857, 19.95382], [50.05858, 19.95374], [50.05861, 19.9535], [50.05876, 19.95173], [50.05878, 19.9515], [50.05881, 19.95107], [50.05884, 19.95061], [50.05883, 19.95048], [50.05883, 19.95008], [50.05881, 19.94974], [50.0588, 19.94952], [50.05879, 19.94901], [50.05879, 19.94884], [50.05878, 19.94874], [50.05875, 19.94851], [50.0587, 19.94821], [50.0587046, 19.948207], [50.05866, 19.94799], [50.05866, 19.94798], [50.05863, 19.94783], [50.05855, 19.94746], [50.05853, 19.94734], [50.05849, 19.94719], [50.05843, 19.94699], [50.0584, 19.94691], [50.05838, 19.94687], [50.0583, 19.94672], [50.058301, 19.9467204], [50.05832, 19.94665], [50.05833, 19.9466], [50.05835, 19.94652], [50.05844, 19.94572], [50.05845, 19.94548], [50.05848, 19.94521], [50.05855, 19.94475], [50.05904, 19.94344], [50.0591, 19.94326], [50.05912, 19.9432], [50.05917, 19.94305], [50.0592, 19.94297], [50.05924, 19.94288], [50.05931, 19.94274], [50.05941, 19.94255], [50.05949, 19.94241], [50.05952, 19.94236], [50.05954, 19.94231], [50.05959, 19.94221], [50.05961, 19.94218], [50.05964, 19.94215], [50.0596365, 19.9421473], [50.05967, 19.94204], [50.05974, 19.94195], [50.05997, 19.94168], [50.06034, 19.94133], [50.06039, 19.94125], [50.06042, 19.94119], [50.06045, 19.94112], [50.06048, 19.94103], [50.06077, 19.94014], [50.06084, 19.93985], [50.0608444, 19.9398549], [50.061, 19.93999], [50.06131, 19.94022], [50.0613077, 19.9402153], [50.0613077, 19.9402153], [50.0613077, 19.9402153]]
    points = [[49.473743, 20.015556], [49.513019, 20.066818]]
    multi_graph = facade.plan_route(
        input=RoutePlanningInput(points=[Point(*point) for point in points], preference=RoutePlanningPreferences())
    )
    print(multi_graph)

    # bike_traffic = facade.get_bike_traffic(preference=RoutePlanningPreferences())
    # print(bike_traffic)