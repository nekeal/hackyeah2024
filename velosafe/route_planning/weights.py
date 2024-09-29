import osmnx as ox

class Weights:
    def __init__(self, safety_factor: int, bike_lane_preference: int):
        self.ROUDTYPE_WEIGHT = safety_factor
        self.MAX_SPEED_WEIGHT = safety_factor
        self.LENGTH_WEIGHT = 1 / safety_factor


    @staticmethod
    def get_weight_by_roadtype(record):

        return ROADTYPE_WEIGHT * roadtype_weights.get(record["highway"], 4)

    @staticmethod
    def get_weight_by_maxspeed(record):
        if record["highway"] in ["primary", "secondary", "tertiary"]:
            if int(record["maxspeed"]) > 30:
                return MAXSPEED_WEIGHT * int(record["maxspeed"]) / 30
        return MAXSPEED_WEIGHT

    @staticmethod
    def get_weight_by_length(record):
        return LENGTH_WEIGHT * record["length"]

    @staticmethod
    def apply_weights(G, *weights):
        nodes, edges = ox.graph_to_gdfs(G)

        edges["weight"] = edges.apply(
            lambda x: sum([fun(x) for fun in weights]), axis=1
        )

        # Normalize
        edges["weight"] = (edges["weight"] - edges["weight"].min()) / (
            edges["weight"].max() - edges["weight"].min()
        )

        G = ox.graph_from_gdfs(nodes, edges)

        return G
