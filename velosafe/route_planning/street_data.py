import osmnx as ox

class StreetData:
    @staticmethod
    def download(city, network_type="all"):
        G_raw = ox.graph_from_place(city, network_type=network_type)
        G = ox.project_graph(G_raw)
        return G

    @staticmethod
    def consolidate_intersections(G):
        G = ox.consolidate_intersections(
            G, rebuild_graph=True, tolerance=15, dead_ends=False
        )
        nodes, edges = ox.graph_to_gdfs(G)
        G = ox.graph_from_gdfs(nodes, edges.explode("highway"))
        return G

    @staticmethod
    def fill_max_speed(G):
        # If no maxspeed available, set 50
        DEFAULT_SPEED = "50"

        # If many speeds available, get the biggest one
        def reduce_max_speed(x):
            if isinstance(x, list):
                return str(max([int(speed) for speed in x]))
            else:
                return x

        nodes, edges = ox.graph_to_gdfs(G)

        edges["maxspeed"] = (
            edges["maxspeed"].fillna(DEFAULT_SPEED).apply(reduce_max_speed)
        )

        G = ox.graph_from_gdfs(nodes, edges)

        return G

    @staticmethod
    def save(G, filename):
        ox.save_graph_geopackage(G, "./data/" + filename)

    @staticmethod
    def load(filename):
        return ox.load_graph_geopackage("./data/" + filename)

    @staticmethod
    def show(G):
        return ox.plot_graph(G)
    
