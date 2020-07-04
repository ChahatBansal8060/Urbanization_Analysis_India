# ---------------------------------------------------------------------

# Copyright © 2020  Chahat Bansal

# All rights reserved

# ----------------------------------------------------------------------

from lxml import etree as ET
from copy import deepcopy
import os, sys

#print("**** Extracting road information from Raw OSM Data *****\n")
'''
The code is automated for all districts, but it is preferred to execute this code for one district at a time.
The large XML files take up the RAM memory. Execute the script one district at a time.
'''
districts = ['Bangalore','Chennai','Delhi','Gurgaon','Hyderabad','Kolkata','Mumbai']
#districts = ['Delhi']

target_directory = "Processed_OSM_data"
os.makedirs( target_directory, exist_ok=True )

for district in districts:
    # print(district)

    encoding = 'utf-8'    
    clean_osm_data_file = open(target_directory+'/processed_'+district+'.osm', "w+")
    clean_osm_data_file.write('<?xml version="1.0" encoding="UTF-8"?>\n<osm version="0.6" generator="Overpass API 0.7.56.2 b688b00f">\n')

    raw_osm_data_path = 'Raw_OSM_data/'+district+'.osm'
    number_of_highway_ways = 0
    number_of_highway_nodes = 0

    context = ET.iterparse(raw_osm_data_path, events=('end',), tag='way')
    final_node_ids = []

    way_string = ""
    for event, elem in context:
        for node_child in elem: # iterating over the sub-elements of a way element
            if node_child.tag == "tag":
                if node_child.attrib["k"] == "highway":
                    number_of_highway_ways += 1
                    way_string += (ET.tostring(elem, pretty_print=True)).decode(encoding)
                    for referred_node in elem:
                        if referred_node.tag == "nd":
                            final_node_ids.append(referred_node.attrib["ref"])
    elem.clear()
        
    del context 
    # print("At this point all ways have been processed")
    # print("Total ways with highway tag: ", number_of_highway_ways)

    final_node_ids = set(final_node_ids)
    context = ET.iterparse(raw_osm_data_path, events=('end',), tag='node')   
    for event, elem in context:
        if elem.attrib["id"] in final_node_ids:
            number_of_highway_nodes += 1
            clean_osm_data_file.write( (ET.tostring(elem, pretty_print=True)).decode(encoding))
        elem.clear()

    del context
    # print("Total nodes with highway tag: ",number_of_highway_nodes)
    clean_osm_data_file.write(way_string)
    clean_osm_data_file.write("</osm>")
    clean_osm_data_file.close()

    print("Road information successfully extracted for ",district)

print("\n#### Check ",target_directory," for the resultant XML Files ####\n")




