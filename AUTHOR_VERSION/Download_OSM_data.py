#THE SCRIPT for automating the OSM data download for districts
import requests
import time
import pandas as pd
import overpy
import os
from math import floor, ceil

'''
Driver code starts here
'''
district_coordinates_dataframe = pd.read_csv("district_coordinates.csv")

districts = (district_coordinates_dataframe["District_Name"].values).tolist()
min_latitudes = (district_coordinates_dataframe["MinLat"].values).tolist()
max_latitudes = (district_coordinates_dataframe["MaxLat"].values).tolist()
min_longitudes = (district_coordinates_dataframe["MinLong"].values).tolist()
max_longitudes = (district_coordinates_dataframe["MaxLong"].values).tolist()

output_directory = "Raw_OSM_data"
os.makedirs(output_directory, exist_ok=True)

for i in range(len(districts)):
    print("Downloading OSM data for district: ",districts[i])
    min_lat = min_latitudes[i] 
    max_lat = max_latitudes[i] 
    min_long = min_longitudes[i]
    max_long = max_longitudes[i] 
    
    rounded_min_lat = floor(100.0 * min_lat) / 100.0
    rounded_max_lat = ceil(100.0 * max_lat) / 100.0
    rounded_min_long = floor(100.0 * min_long) / 100.0
    rounded_max_long = ceil(100.0 * max_long) / 100.0

    query = 'https://overpass-api.de/api/map?bbox='+str(rounded_min_long)+','+str(rounded_min_lat)+','+str(rounded_max_long)+','+str(rounded_max_lat)
    
    output_file_path = output_directory+'/'+districts[i]+'.osm'
    os.system('wget -O '+output_file_path+' '+query)

    #Test if complete data is downloaded from OSM
    file_object = open(output_file_path)
    osm_text = file_object.read().strip().split()
    if '</osm>' in osm_text:
        print("Complete OSM data downloaded for district: ",districts[i])
    else:
        print("Incomplete OSM data downloaded for district: ",districts[i])



