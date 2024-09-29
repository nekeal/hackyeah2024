import osmnx as ox
import networkx as nx

class Route:
    @staticmethod
    def find(G, start, end):
        nodes, edges = ox.graph_to_gdfs(G)
        sp_nodes = nx.dijkstra_path(G, start, end, weight="weight")
        sp_edges = list(nx.utils.pairwise(sp_nodes))
        nodes = nodes[nodes.index.isin(sp_nodes)]
        edges = edges[edges.index.isin(sp_edges)]

        index = edges.groupby(by=["u", "v"])["weight"].idxmin()
        edges = edges[edges.index.isin(index)]

        return ox.graph_from_gdfs(nodes, edges)
