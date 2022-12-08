import numpy as np
import heapq
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
from keys import google_elevation_api_key
from utils import *
import networkx as nx


def find_route(source, dest, place, method='A', percentage=1, min_max=1):
    # place = "Piedmont, California, USA"
    G = ox.graph_from_place(place, network_type="all")
    G = ox.elevation.add_node_elevations_google(
        G, api_key=google_elevation_api_key)
    G = ox.elevation.add_edge_grades(G)
    print(source)
    print(dest)
    orig_node = ox.nearest_nodes(G, source[0], source[1])
    dest_node = ox.nearest_nodes(G, dest[0], dest[1])
    print(orig_node)
    print(dest_node)

    # dest_node = ox.nearest_nodes((dest['x'], dest['y']))
    route = ox.shortest_path(G, orig_node, dest_node, weight="length")

    routes = get_route_coord(G, route)
    route_length = get_path_length(G, route)
    elevation_g = get_path_elevation(G, route)

    return routes, route_length, elevation_g


def Astar(source, dest, min_max, max_length, place):
    # intial the map
    G = ox.graph_from_place(place, network_type="all")
    G = ox.elevation.add_node_elevations_google(
        G, api_key=google_elevation_api_key)

    G = ox.elevation.add_edge_grades(G)

    # create source and destination node
    start = ox.nearest_nodes(G, source[0], source[1])
    end = ox.nearest_nodes(G, dest[0], dest[1])

    open_list = [NodeWrapper(start)]
    close_list = set()
    visited_node = {start: NodeWrapper(start)}
    while (len(open_list) > 0):
        curr_node = heapq.heappop(open_list)
        close_list.add(curr_node.id)

        if (curr_node.id == end):
            path = []
            curr = curr_node
            while curr.parent is not None:
                path.insert(0, curr.id)
                curr = visited_node[curr.parent]
            path.insert(0, curr.id)
            routes = get_route_coord(G, path)
            route_length = get_path_length(G, path)
            elevation_g = get_path_elevation(G, path)
            return routes, route_length, elevation_g

        successors = filter(lambda n: n not in close_list,
                            nx.neighbors(G, curr_node.id))
        for successor in successors:
            distance = curr_node.curr_dist + \
                get_length(G, curr_node.id, successor)
            if distance <= max_length:
                flag = successor in visited_node
                pred_distance = distance + \
                    get_heuristic_distance(G, successor, end)
                elevation_gain = curr_node.elevation + \
                    get_elevation_gain(G, curr_node.id, successor)
                successor_node = NodeWrapper(
                    successor, curr_node.id, distance, pred_distance, elevation_gain, open_list)
                visited_node[successor] = successor_node

                if flag:
                    heapq.heapify(open_list)
                else:
                    heapq.heappush(open_list, successor_node)
    return []


# if __name__ == "__main__":
#     place = "Amherst, Massachusetts, USA"
#     source = [-72.5198118276834, 42.373051188825855]
#     dest = [-72.4992091462399, 42.36979729154845]

#     route1, r1_length, elevation1 = find_route(source, dest, place)
#     route2, r2_length, elevation2 = Astar(
#         source, dest, 1, r1_length*1.5, place)

#     if (route1 == route2):
#         print("same")
#     else:
#         print("different")
#     print("done!")
