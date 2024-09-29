import osmnx as ox


class Weights:
    def __init__(self, safety_factor: int, bike_lane_preference: int, street_lights: bool | None = None):
        self.ROADTYPE_WEIGHT = 5 * (safety_factor - 1) ** 2
        self.MAX_SPEED_WEIGHT = 5 * (safety_factor - 1) ** 2
        self.LENGTH_WEIGHT = 1
        self.STREET_LIGHTS_WEIGHT = 10 if street_lights is True else 0
        self.ROADTYPE_WEIGHTS = {
            "cycleway": 1,
            "path": 1,
            "pedestrian": 1,
            "track": 1,
            "unclassified": 1.5 * bike_lane_preference,
            "residential": 1.5 * bike_lane_preference,
            "living_street": 1.5 * bike_lane_preference,
            "tertiary": 1.5 * bike_lane_preference,
            "secondary": 2 * bike_lane_preference,
            "primary": 3 * bike_lane_preference,
            "_other": 1.5 * bike_lane_preference,
        }

    def get_weight_by_roadtype(self, record):
        return self.ROADTYPE_WEIGHT * self.ROADTYPE_WEIGHTS.get(record["highway"], self.ROADTYPE_WEIGHTS["_other"])

    def get_weight_by_maxspeed(self, record):
        if record["highway"] in ["primary", "secondary", "tertiary"]:
            if int(record["maxspeed"]) > 30:
                return self.MAX_SPEED_WEIGHT * int(record["maxspeed"]) / 30
        return self.MAX_SPEED_WEIGHT

    def get_weight_by_length(self, record):
        return self.LENGTH_WEIGHT * record["length"]
    
    def get_weight_by_street_lights(self, record):
        return self.STREET_LIGHTS_WEIGHT * (1 if record['street_lights'] else 0)

    def apply_weights(G, *weights):
        nodes, edges = ox.graph_to_gdfs(G)

        edges["weight"] = edges.apply(lambda x: sum([fun(x) for fun in weights]), axis=1)

        # Normalize
        edges["weight"] = (edges["weight"] - edges["weight"].min()) / (edges["weight"].max() - edges["weight"].min())

        G = ox.graph_from_gdfs(nodes, edges)

        return G
