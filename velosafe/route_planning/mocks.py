import osmnx as ox

class StreetDataMocks:
    @staticmethod
    def mock_street_lights(G):
        nodes, edges = ox.graph_to_gdfs(G)
        edges['street_lights'] = False
        return ox.graph_from_gdfs(nodes, edges)
