# ---------------------------------------------------------------------

# Copyright © 2020  Chahat Bansal

# All rights reserved

# ----------------------------------------------------------------------

from lxml import etree as ET
from copy import deepcopy
import os, sys
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt, floor, ceil
from queue import PriorityQueue
import random
from statistics import mean


'''
This function creates a mapping which stores node id as key and node's information as value. 
The value is again stored as a key/value map which stores the details corresponding to this node.
Every long and lat value in this has a precision of 7 decimal points
'''
def Extract_node_details(input_directory, processed_OSM_datafile):
    input_file_path = input_directory+'/'+processed_OSM_datafile
    context = ET.iterparse(input_file_path, events=('end',), tag='node')
    node_information_map = {}

    for event, node in context:
        if( node.attrib["id"] not in node_information_map):
            node_information_map[ node.attrib["id"] ] = {}
            node_information_map[ node.attrib["id"] ]["lat"] = float(node.attrib["lat"])
            node_information_map[ node.attrib["id"] ]["lon"] = float(node.attrib["lon"])
        node.clear()
    return node_information_map


'''
This function creates the adjacency list corresponding to the road network of each district
Inputs:
1) input_directory = name of directory holding the processed OSM data on Roads
2) processed_OSM_datafile = name of the file holding processed OSM data for particular district
3) min_lat = minimum latitude of district bounding box
3) max_lat = maximum latitude of district bounding box
3) min_lon = minimum longitude of district bounding box
3) max_lon = maximum longitude of district bounding box
'''
def Create_adjacency_list(input_directory, processed_OSM_datafile, min_lat, max_lat, min_lon, max_lon):
    input_file_path = input_directory+'/'+processed_OSM_datafile
    context = ET.iterparse(input_file_path, events=('end',), tag='way')
    adjacency_list = {}
    
    for event, ways in context:
        for i in range(len(ways)):
            if ways[i].tag == 'nd' and ways[i+1].tag == 'nd':
                
                node1_lat = node_information_map[ways[i].attrib["ref"]]['lat']
                node1_lon = node_information_map[ways[i].attrib["ref"]]['lon']
                node2_lat = node_information_map[ways[i+1].attrib["ref"]]['lat']
                node2_lon = node_information_map[ways[i+1].attrib["ref"]]['lon']
                
                # If nodes are outside the bounding box of the district, exclude the edges associated with them
                if (node1_lat < min_lat or node1_lat > max_lat or node1_lon < min_lon or node1_lon > max_lon):
                    outside_node1 = True
                else:
                    outside_node1 = False

                if (node2_lat < min_lat or node2_lat > max_lat or node2_lon < min_lon or node2_lon > max_lon):
                    outside_node2 = True
                else:
                    outside_node2 = False

                # if source node lies within the bounding box
                if outside_node1 == False:
                    if ways[i].attrib["ref"] not in adjacency_list:
                        adjacency_list[ways[i].attrib["ref"]] = []
                    if outside_node2 == False:
                        if ways[i+1].attrib["ref"] not in adjacency_list[ways[i].attrib["ref"]]: 
                            adjacency_list[ways[i].attrib["ref"]].append(ways[i+1].attrib["ref"])

                # if destination node lies within the bounding box
                if outside_node2 == False:
                    if ways[i+1].attrib["ref"] not in adjacency_list:
                        adjacency_list[ways[i+1].attrib["ref"]] = []
                    if outside_node1 == False:
                        if ways[i].attrib["ref"] not in adjacency_list[ways[i+1].attrib["ref"]]: 
                            adjacency_list[ways[i+1].attrib["ref"]].append(ways[i].attrib["ref"])
        ways.clear()    
    return adjacency_list

'''
Getting the latitude and longitude bounding box of the district
Since the coordinate information of nodes in OSM data has precision 7, we round off coordinates to same precision
'''
def Get_district_bounding_box( district_coordinates_filepath, district ):        
    bounding_box_dataframe = pd.read_csv(district_coordinates_filepath)
    district_index = np.where( bounding_box_dataframe["District_Name"].values == district )
    
    min_lat = float( (bounding_box_dataframe["MinLat"].values)[district_index] )
    max_lat = float( (bounding_box_dataframe["MaxLat"].values)[district_index] )
    min_lon = float( (bounding_box_dataframe["MinLong"].values)[district_index] )
    max_lon = float( (bounding_box_dataframe["MaxLong"].values)[district_index] )
    
    # Since the grid size (0.01) is of precision 2, round off the image bounding box to fit all the grids
    rounded_min_lat = floor(100.0 * min_lat) / 100.0
    rounded_max_lat = ceil(100.0 * max_lat) / 100.0
    rounded_min_lon = floor(100.0 * min_lon) / 100.0
    rounded_max_lon = ceil(100.0 * max_lon) / 100.0

    return rounded_min_lat, rounded_max_lat, rounded_min_lon, rounded_max_lon


'''
This function returns the adjacency list corresponding to a grid
Input parameters-
1) min_lat = minimum latitude value for this grid (y-axis)
2) max_lat = maximum latitude value for this grid which is (min_lat + grid_size)
3) min_long = minimum longitude value for this grid (x-axis)
3) max_long = maximum longitude value for this grid which is (min_long + grid_size)
4) node_information_map = contains node id as key and it's coordinates as value
5) adjacency list = contains the adjacency list of all nodes in the district
Output-
1) grid_adjacency_list_full_edges = It stores each edge lying fully within grid TWICE
2) grid_adjacency_list_half_edges = It stores edges with one node within grid, ONCE
'''
def Get_grid_adjacency_list(min_lat, max_lat, min_long, max_long, node_information_map, adjacency_list):
    grid_adjacency_list_full_edges = {} # This map stores full edges inside the grid
    grid_adjacency_list_half_edges = {} # This map stores the edges with only one node inside the grid

    for source_node_id in adjacency_list.keys():
        source_node_lat = node_information_map[source_node_id]["lat"]
        source_node_long = node_information_map[source_node_id]["lon"]
        # If the coordinates of the source node lie anywhere outside the grid, ignore this node
        if source_node_lat < min_lat or source_node_lat > max_lat or source_node_long < min_long or source_node_long > max_long:
            continue
        
        # If the coordinates of the source node lie within the grid add it to adjacency list
        if source_node_id not in grid_adjacency_list_full_edges:
            grid_adjacency_list_full_edges[source_node_id] = []
        
        # check destination node, if it is also in grid, add to full edge, else to half edge
        for destination_node_id in adjacency_list[source_node_id]:
            dest_lat = node_information_map[destination_node_id]["lat"] 
            dest_lon = node_information_map[destination_node_id]["lon"]
            
            # half edge
            if dest_lat < min_lat or dest_lat > max_lat or dest_lon < min_long or dest_lon > max_long:
                if source_node_id not in grid_adjacency_list_half_edges:
                    grid_adjacency_list_half_edges[source_node_id] = []
                grid_adjacency_list_half_edges[source_node_id].append(destination_node_id)
                continue
            
            # full edge
            grid_adjacency_list_full_edges[source_node_id].append(destination_node_id)

    return grid_adjacency_list_full_edges, grid_adjacency_list_half_edges


'''
This function returns the count of 3-way and 4-way intersections in a grid using its adjacency list
Inputs:
1) grid_adjacency_list_full_edges = map of all edges lying completely within the grid
2) grid_adjacency_list_half_edges = map of edges lying partially within a grid
'''    
def Get_intersection_count(grid_adjacency_list_full_edges, grid_adjacency_list_half_edges):
    three_way_intersections = 0
    four_way_intersections = 0
    for source_node_id in grid_adjacency_list_full_edges.keys():
        source_node_degree = len(grid_adjacency_list_full_edges[source_node_id]) #initializing
        if source_node_id in grid_adjacency_list_half_edges:
            source_node_degree += len(grid_adjacency_list_half_edges[source_node_id])

        if source_node_degree == 3:
            three_way_intersections += 1
        if source_node_degree == 4:
            four_way_intersections += 1
    
    return three_way_intersections, four_way_intersections


'''
This function is used to find the distance between two coordinates on earth using Haversine formula
'''
def Get_distance(source_lat, source_lon, dest_lat, dest_lon):
    # convert all coordinates from degrees to radians
    source_lat = radians(source_lat)
    source_lon = radians(source_lon)
    dest_lat = radians(dest_lat)
    dest_lon = radians(dest_lon)
    
    # Applying Haversine formula
    difference_lat = dest_lat - source_lat
    difference_lon = dest_lon - source_lon
    a = sin(difference_lat/2)**2 + cos(source_lat) * cos(dest_lat) * sin(difference_lon / 2)**2
    c = 2 * asin(sqrt(a))
    earth_radius = 6378100.0 # Radius of earth in meters. Use 3956 for miles
    
    return c * earth_radius


'''
This function is used to compute the road length of each grid
'''
def Get_road_length(min_grid_lat, min_grid_lon, grid_size, node_information_map, grid_adjacency_list_full_edges, grid_adjacency_list_half_edges):
    total_grid_road_length = 0.0 #initializing
    
    # Calculating distance of full edges lying inside the grid. 
    for source_node_id in grid_adjacency_list_full_edges.keys():
        source_lat = node_information_map[source_node_id]["lat"]
        source_lon = node_information_map[source_node_id]["lon"]
        for destination_node_id in grid_adjacency_list_full_edges[source_node_id]:
            dest_lat = node_information_map[destination_node_id]["lat"]
            dest_lon = node_information_map[destination_node_id]["lon"]            
            total_grid_road_length += Get_distance(source_lat, source_lon, dest_lat, dest_lon)  
    
    # The total distance is halved because an undirected adjacency list has each edge added twice
    total_grid_road_length = total_grid_road_length/2.0
    #Calculating distance of half edges after interpolation
    max_grid_lat = min_grid_lat + grid_size
    max_grid_lon = min_grid_lon + grid_size
    
    for source_node_id in grid_adjacency_list_half_edges.keys():
        source_lat = node_information_map[source_node_id]["lat"]
        source_lon = node_information_map[source_node_id]["lon"]
        for destination_node_id in grid_adjacency_list_half_edges[source_node_id]:
            dest_lat = node_information_map[destination_node_id]["lat"]
            dest_lon = node_information_map[destination_node_id]["lon"]
            # First find where out of the immediate 4 neighbouring grids does the destination node lie 
            # and interpolate using standard formula of linear equations
            if (dest_lat < min_grid_lat and dest_lon >= min_grid_lon and dest_lon <= max_grid_lon): # bottom grid
                interpolated_lat = min_grid_lat
                interpolated_lon = ( ((min_grid_lat - source_lat)*(dest_lon - source_lon)) / (dest_lat - source_lat) )+source_lon
                total_grid_road_length += Get_distance(source_lat, source_lon, interpolated_lat, interpolated_lon)
        
            elif (dest_lat > max_grid_lat and dest_lon >= min_grid_lon and dest_lon <= max_grid_lon): # top grid
                interpolated_lat = max_grid_lat
                interpolated_lon = ( ((max_grid_lat - source_lat)*(dest_lon - source_lon)) / (dest_lat - source_lat) )+source_lon
                total_grid_road_length += Get_distance(source_lat, source_lon, interpolated_lat, interpolated_lon)
        
            elif (dest_lon < min_grid_lon and dest_lat >= min_grid_lat and dest_lat <= max_grid_lat): # left grid
                interpolated_lon = min_grid_lon
                interpolated_lat = ( ((min_grid_lon - source_lon)*(dest_lat - source_lat)) / (dest_lon - source_lon) )+source_lat
                total_grid_road_length += Get_distance(source_lat, source_lon, interpolated_lat, interpolated_lon)
            
            elif (dest_lon > max_grid_lon and dest_lat >= min_grid_lat and dest_lat <= max_grid_lat): # right grid
                interpolated_lon = max_grid_lon
                interpolated_lat = ( ((max_grid_lon - source_lon)*(dest_lat - source_lat)) / (dest_lon - source_lon) )+source_lat
                total_grid_road_length += Get_distance(source_lat, source_lon, interpolated_lat, interpolated_lon)
    return total_grid_road_length


'''
This function returns all the edges in the bounding box surrounding the current grid which includes its 8 neighbours
Inputs:
1) curr_lat = minimum latitude value of current grid
2) curr_lon = minimum longitude value of current grid
3) grid_size = size of the grid (in degrees)
4) min_lat = minimum latitude value of the district bounding box
5) max_lat = maximum latitude value of the district bounding box
6) min_lon = minimum longitude value of the district bounding box
7) max_lon = maximum longitude value of the district bounding box
8) node_information_map = a map storing coordinates of each node against its id as key
9) adjacency_list = an adjacency list of all edges in the entire district
'''
def Get_neighbour_adjacency_list(curr_lat, curr_lon, grid_size, min_lat, max_lat, min_lon, max_lon, node_information_map, adjacency_list):
    neigh_box_min_lon = curr_lon - grid_size
    neigh_box_max_lon = curr_lon + (2*grid_size)
    neigh_box_min_lat = curr_lat - grid_size
    neigh_box_max_lat = curr_lat + (2*grid_size)
    
    # testing the neighbour bounding box coordinates against district coordinates
    if neigh_box_min_lon < min_lon:
        neigh_box_min_lon = min_lon
    if neigh_box_max_lon > max_lon:
        neigh_box_max_lon = max_lon
    if neigh_box_min_lat < min_lat:
        neigh_box_min_lat = min_lat
    if neigh_box_max_lat > max_lat:
        neigh_box_max_lat = max_lat
        
    full_edge_list, half_edge_list = Get_grid_adjacency_list(neigh_box_min_lat, neigh_box_max_lat, neigh_box_min_lon, neigh_box_max_lon, node_information_map, adjacency_list)
    
    return full_edge_list


'''
This function is used to return the nearest OSM node to the given pair of coordinates in a grid
Input:
1) lat_value = randomly generated latitude value
2) lon_value = randomly generated longitude value
3) adjacency_list = adjacency list corresponding to the road network in the grid
4) node_information_map = coordinate information of all osm nodes in the district 
'''
def Get_nearest_node(lat_value, lon_value, adjacency_list, node_information_map):
    minimum_distance = 1e10 # assign initial value as high as some infinity point in integers
    nearest_node_id = -1
    
    for node_id in adjacency_list.keys():
        node_lat = node_information_map[node_id]["lat"]
        node_lon = node_information_map[node_id]["lon"]
        distance = Get_distance(lat_value, lon_value, node_lat, node_lon)
        if distance < minimum_distance:
            minimum_distance = distance
            nearest_node_id = node_id
    
    return nearest_node_id, minimum_distance


'''
This function uses dijkstra's algortihm to find the shortest path between 2 nodes
Inputs:
1) source_node_id = The source node id
2) dest_node_id = The destination node id
3) adjacency_list = Adjacency list corresponding to the nodes in the neighbouring bounding box of a grid
4) node_information_map = It stores the coordinate values of each node in the district
Output:
1) distance_map[dest_node_id] = It stores the shortest distance between the source and destination nodes. 
0.0 value in return value means no shortest path available
'''
def dijkstra(source_node_id, dest_node_id, adjacency_list, node_information_map):
    distance_map = {} #this will store the distance to each node from the source node. key=node_id, value= distance in km
    visited_node_ids = []
        
    # initializing distance map
    for node_id in adjacency_list:
        if node_id not in distance_map:
            distance_map[node_id] = 1e10 # initialize all distances to infinity
                    
    distance_map[source_node_id] = 0
    priority_queue = PriorityQueue()
    priority_queue.put( (distance_map[source_node_id], source_node_id) )
    
    while not priority_queue.empty():
        curr_node = priority_queue.get()
        curr_node_id = curr_node[1]
        curr_node_distance = curr_node[0]
        visited_node_ids.append(curr_node_id)
        if curr_node_distance > distance_map[curr_node_id]:
            continue
        if curr_node_id == dest_node_id:
            break
        # add adjacent nodes of the current node to the priority queue
        for adjacent_node_id in adjacency_list[curr_node_id]:
            if adjacent_node_id not in visited_node_ids:
                # find distance between adjacent_node_id and curr_node_id
                curr_node_lat = node_information_map[curr_node_id]["lat"]
                curr_node_lon = node_information_map[curr_node_id]["lon"]
                adjacent_node_lat = node_information_map[adjacent_node_id]["lat"]
                adjacent_node_lon = node_information_map[adjacent_node_id]["lon"]
                edge_weight = Get_distance(curr_node_lat, curr_node_lon, adjacent_node_lat, adjacent_node_lon)
                
                if distance_map[curr_node_id] + edge_weight < distance_map[adjacent_node_id]:
                    distance_map[adjacent_node_id] = distance_map[curr_node_id] + edge_weight
                    priority_queue.put( (distance_map[adjacent_node_id], adjacent_node_id) )
            
    return distance_map[dest_node_id] 


'''
This function is used to calculate the walkability ratio of each grid
Inputs:
1) curr_lat = minimum latitude value of current grid
2) curr_lon = minimum longitude value of current grid
3) grid_size = size of the grid (in degrees)
4) min_lat = minimum latitude value of the district bounding box
5) max_lat = maximum latitude value of the district bounding box
6) min_lon = minimum longitude value of the district bounding box
7) max_lon = maximum longitude value of the district bounding box
8) node_information_map = a map storing coordinates of each node against its id as key
9) adjacency_list = an adjacency list of all edges in the entire district
10) grid_adjacency_list = adjacency list of nodes belonging to the grid
Output:
1) walkability_ratio = The walkability ratio of the current grid
'''
def Get_walkability_ratio(curr_lat, curr_lon, grid_size, min_lat, max_lat, min_lon, max_lon, node_information_map, adjacency_list, grid_adjacency_list):
    # get all the edges lying in the bounding box of grid and all its 8 neighouring grids
    neighbours_adjacency_list = Get_neighbour_adjacency_list(curr_lat, curr_lon, grid_size, min_lat, max_lat, min_lon, max_lon, node_information_map, adjacency_list)
        
    epochs = 10
    number_of_pairs = 20
    
    epoch_walkability_ratio_list = []
    for epoch in range(epochs):
        pair_walkability_ratio_list = []
        for pair in range(number_of_pairs):
            source_lat = random.uniform( curr_lat, (curr_lat+grid_size) )
            source_lon = random.uniform( curr_lon, (curr_lon+grid_size) )
            dest_lat = random.uniform( curr_lat, (curr_lat+grid_size) )
            dest_lon = random.uniform( curr_lon, (curr_lon+grid_size) )
            
            beeline_distance = Get_distance(source_lat, source_lon, dest_lat, dest_lon)
            
            source_node_id, source_distance = Get_nearest_node(source_lat, source_lon, neighbours_adjacency_list, node_information_map)
            dest_node_id, dest_distance = Get_nearest_node(dest_lat, dest_lon, neighbours_adjacency_list, node_information_map)
            
            if source_node_id != -1 and dest_node_id != -1: 
                shortest_path = dijkstra(source_node_id, dest_node_id, neighbours_adjacency_list, node_information_map)
                shortest_path = shortest_path + source_distance + dest_distance
            else:
                shortest_path = 0.0

            if (shortest_path): # if shortest distance is not zero
                walkability_ratio = beeline_distance / shortest_path
                pair_walkability_ratio_list.append(walkability_ratio)
        
        if len(pair_walkability_ratio_list) > 0:
            average_walkability_ratio = mean(pair_walkability_ratio_list)
            epoch_walkability_ratio_list.append( average_walkability_ratio )
    
    if len(epoch_walkability_ratio_list) > 0:
        walkability_ratio = mean(epoch_walkability_ratio_list)
    else:
        walkability_ratio = 0.0
        
    return round(walkability_ratio, 4)


'''
Driver code starts here
'''
print("***** Calculating Grid-level Road-based Indicators ******\n")
districts = ['Chennai', 'Bangalore', 'Delhi','Gurgaon','Hyderabad','Kolkata','Mumbai']

for district in districts:
    # print(district)

    input_directory = 'Processed_OSM_data'
    processed_OSM_datafile = 'processed_'+district+'.osm'

    min_lat, max_lat, min_lon, max_lon = Get_district_bounding_box( 'district_coordinates.csv', district )
    node_information_map = Extract_node_details(input_directory, processed_OSM_datafile)
    adjacency_list = Create_adjacency_list(input_directory, processed_OSM_datafile, min_lat, max_lat, min_lon, max_lon)

    # The following lists will store the final results which will be dumped to an excel file
    result_grid_numbers = []
    result_grid_coordinates = []
    result_three_ways = []
    result_four_ways = []
    result_road_lengths = []
    result_walkability_ratio = []

    grid_number = 0
    # We will iterate through the latitude and longitude range in integers to prevent the issues with float precision
    for longitude in range( round(min_lon*100), round(max_lon*100), round(0.01*100) ):
        for latitude in range( round(min_lat*100), round(max_lat*100), round(0.01*100) ):
            curr_lat = latitude/100
            curr_long = longitude/100
            
            grid_adjacency_list_full_edges, grid_adjacency_list_half_edges = Get_grid_adjacency_list(curr_lat, curr_lat + 0.01, curr_long, curr_long + 0.01, node_information_map, adjacency_list)
            
            three_ways, four_ways = Get_intersection_count(grid_adjacency_list_full_edges, grid_adjacency_list_half_edges)
            grid_road_length = Get_road_length(curr_lat, curr_long, 0.01, node_information_map, grid_adjacency_list_full_edges, grid_adjacency_list_half_edges)
            grid_road_length = round(grid_road_length, 4)
            walkability_ratio = Get_walkability_ratio(curr_lat, curr_long, 0.01, min_lat, max_lat, min_lon, max_lon, node_information_map, adjacency_list, grid_adjacency_list_full_edges)
            # print("Grid ",grid_number,"- \t 3-ways: ",three_ways,"\t 4-ways: ",four_ways,"\t Road Length: ",grid_road_length,"\t walkability ratio: ", walkability_ratio)
                
            result_grid_numbers.append(grid_number)
            result_grid_coordinates.append([curr_lat, curr_long])
            result_three_ways.append(three_ways)
            result_four_ways.append(four_ways)
            result_road_lengths.append(grid_road_length)
            result_walkability_ratio.append(walkability_ratio)
            
            grid_number += 1

    results_directory = "Grid_wise_road_indicators"
    os.makedirs(results_directory, exist_ok = True)

    result_filename = district+"_road_indicators.csv"

    Zipped_results =  list(zip(result_grid_numbers, result_grid_coordinates, result_three_ways, result_four_ways, result_road_lengths, result_walkability_ratio))
    Results_dataframe = pd.DataFrame(Zipped_results, columns = ['Grid_number', 'Grid_coordinates', 'Three_ways', 'Four_ways', 'Road_length', 'Walkability_ratio'])

    Results_dataframe.to_csv(results_directory+'/'+result_filename, index=False)
    print("Road indicators calculated successfully for ",district)

print("Execution Complete!\n")



